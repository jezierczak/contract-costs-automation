import logging
from dataclasses import replace

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.contracts.migration.backfill_system_contracts_command import BackfillSystemContractsCommand
from contract_costs.services.documents.scoring.simple_scoring_policy import SimpleScoringPolicy
from contract_costs.services.financial_records.migration.backfill_import_payments_command import (
    BackfillImportPaymentsCommand,
)

logger = logging.getLogger(__name__)


def build_system_commands(subparsers):
    p = subparsers.add_parser(
        "backfill",
        help="Ensure system contracts exist for OWN companies",
    )
    p.set_defaults(handler=handle_system_backfill)

    p2 = subparsers.add_parser(
        "calculate-document-score",
        help="Recalculate scoring for documents with parsed payload",
    )

    # 👇 NOWA FLAGA
    p2.add_argument(
        "--force",
        action="store_true",
        help="Recalculate score even if already exists",
    )

    p2.set_defaults(handler=handle_calculate_document_score)

    p3 = subparsers.add_parser(
        "backfill-import-payments",
        help="Find records paid at sale (cash/card/BLIK/bon/pre-paid) or PAID without payments; "
             "dry-run unless --apply",
    )
    p3.add_argument(
        "--apply",
        action="store_true",
        help="Add the missing payments (default: only list what would change)",
    )
    p3.set_defaults(handler=handle_backfill_import_payments)


REGISTRY.register_group("system", build_system_commands)


def handle_system_backfill(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    services.action_bus.execute(
        action=BackfillSystemContractsCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        ),
        handler=services.backfill_system_contracts,
    )

    print(f"System contracts ensured for organization {organization_id}")


def handle_calculate_document_score(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
    except ContextError:
        return

    scoring_policy = SimpleScoringPolicy()

    updated = 0
    skipped = 0
    failed = 0

    with services._factory.unit_of_work() as uow:

        documents = uow.documents.list_filtered(
            organization_id=organization_id,
            has_payload=True,
        )

        for document in documents:

            # 👇 NOWA LOGIKA
            if document.scoring is not None and not args.force:
                skipped += 1
                continue

            try:
                scoring = scoring_policy.calculate(
                    document.parsed_payload,
                    is_structured_xml=document.document_source.name == "KSEF"
                )

                updated_doc = replace(document, scoring=scoring)

                uow.documents.update(updated_doc)
                updated += 1

            except Exception:
                logger.exception(
                    "Failed recalculating score for document %s",
                    document.id,
                )
                failed += 1

        uow.commit()

    print("----- Document scoring backfill -----")
    print(f"Updated: {updated}")
    print(f"Skipped: {skipped}")
    print(f"Failed:  {failed}")
    print(f"Organization: {organization_id}")


def handle_backfill_import_payments(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    fixes = services.action_bus.execute(
        action=BackfillImportPaymentsCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            apply=args.apply,
        ),
        handler=services.backfill_import_payments,
    )

    print(f"{'REFERENCJA':<30} {'DATA':<10} {'FORMA':<13} {'STATUS':<14} {'DO ZAPŁATY':>12} {'WPŁACONO':>12} {'DOPŁATA':>12} DATA ZAPŁATY")
    for fix in sorted(fixes, key=lambda f: (f.invoice_date is None, f.invoice_date, f.reference)):
        print(
            f"{fix.reference[:30]:<30} {str(fix.invoice_date or '—'):<10} "
            f"{fix.payment_method.value:<13} {fix.payment_status.value:<14} "
            f"{fix.payable:>12} {fix.already_paid:>12} {fix.missing:>12} {fix.paid_date}"
        )

    total_missing = sum((f.missing for f in fixes), 0)
    print(f"----- Rekordów: {len(fixes)}, suma dopłat: {total_missing} -----")
    if args.apply:
        print("Zapisano wpłaty i przeliczono statusy.")
    else:
        print("Tryb podglądu – nic nie zapisano. Uruchom z --apply, żeby naprawić.")
