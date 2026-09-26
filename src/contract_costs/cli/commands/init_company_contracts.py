import logging
from dataclasses import replace

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.companies.migration.delete_unused_companies_command import DeleteUnusedCompaniesCommand
from contract_costs.services.contracts.migration.backfill_system_contracts_command import BackfillSystemContractsCommand
from contract_costs.services.documents.scoring.simple_scoring_policy import SimpleScoringPolicy
from contract_costs.services.documents.migration.repair_document_paths_command import RepairDocumentPathsCommand
from contract_costs.services.documents.migration.repair_orphan_documents_command import RepairOrphanDocumentsCommand
from contract_costs.services.financial_records.migration.backfill_import_payments_command import (
    BackfillImportPaymentsCommand,
)
from contract_costs.services.financial_records.migration.repair_record_companies_command import (
    RepairRecordCompaniesCommand,
)
from contract_costs.services.financial_records.migration.repair_record_companies_service import RepairKind

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

    p4 = subparsers.add_parser(
        "repair-document-paths",
        help="Fix document paths with trailing dots/spaces (Windows vs container dirs); "
             "run inside the container; dry-run unless --apply",
    )
    p4.add_argument(
        "--apply",
        action="store_true",
        help="Move files and update paths (default: only list what would change)",
    )
    p4.set_defaults(handler=handle_repair_document_paths)

    p5 = subparsers.add_parser(
        "repair-record-companies",
        help="Re-parse KSeF XML of attached documents and re-link records whose seller/buyer "
             "has a different NIP; run inside the container; dry-run unless --apply",
    )
    p5.add_argument(
        "--apply",
        action="store_true",
        help="Re-link unambiguous records (default: only list what would change)",
    )
    p5.set_defaults(handler=handle_repair_record_companies)

    p6 = subparsers.add_parser(
        "delete-unused-companies",
        help="Delete non-OWN companies without records, contracts or KSeF settings; "
             "dry-run unless --apply",
    )
    p6.add_argument(
        "--apply",
        action="store_true",
        help="Delete the listed companies (default: only list them)",
    )
    p6.set_defaults(handler=handle_delete_unused_companies)

    p7 = subparsers.add_parser(
        "repair-orphan-documents",
        help="Return APPLIED documents whose record no longer exists to READY (file back to raw); "
             "run inside the container; dry-run unless --apply",
    )
    p7.add_argument(
        "--apply",
        action="store_true",
        help="Move files and set READY (default: only list them)",
    )
    p7.set_defaults(handler=handle_repair_orphan_documents)


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


def handle_repair_document_paths(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    fixes = services.action_bus.execute(
        action=RepairDocumentPathsCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            apply=args.apply,
        ),
        handler=services.repair_document_paths,
    )

    for fix in sorted(fixes, key=lambda f: (f.kind.value, f.old_path)):
        print(f"{fix.kind.value:<10} {fix.old_path}")
        print(f"{'':<10} -> {fix.new_path}")

    counts = {kind: sum(1 for f in fixes if f.kind == kind) for kind in {f.kind for f in fixes}}
    summary = ", ".join(f"{kind.value}: {count}" for kind, count in sorted(counts.items(), key=lambda i: i[0].value))
    print(f"----- Dokumentów: {len(fixes)} ({summary or 'brak'}) -----")
    if args.apply:
        print("Zapisano (missing pominięte – do ręcznego sprawdzenia).")
    else:
        print("Tryb podglądu – nic nie zapisano. Uruchom z --apply, żeby naprawić.")



def _company_label(company) -> str:
    if company is None:
        return "—"
    return f"{company.name} ({company.tax_number})"


def handle_repair_record_companies(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    fixes = services.action_bus.execute(
        action=RepairRecordCompaniesCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            apply=args.apply,
        ),
        handler=services.repair_record_companies,
    )

    for fix in sorted(fixes, key=lambda f: (f.kind.value, f.reference)):
        side = fix.side.value if fix.side else "—"
        print(f"{fix.kind.value:<16} {fix.reference[:30]:<30} {side:<6} NIP z XML: {', '.join(fix.xml_tax_numbers) or '—'}")
        print(f"{'':<16} jest:   {_company_label(fix.current_company)}")
        if fix.target_company:
            print(f"{'':<16} będzie: {_company_label(fix.target_company)}")
        if fix.detail:
            print(f"{'':<16} {fix.detail}")

    counts = {kind: sum(1 for f in fixes if f.kind == kind) for kind in {f.kind for f in fixes}}
    summary = ", ".join(f"{kind.value}: {count}" for kind, count in sorted(counts.items(), key=lambda i: i[0].value))
    print(f"----- Pozycji: {len(fixes)} ({summary or 'brak'}) -----")
    if args.apply:
        print(f"Przepięto pozycje {RepairKind.FIX.value}; pozostałe do ręcznego sprawdzenia.")
    else:
        print("Tryb podglądu – nic nie zapisano. Uruchom z --apply, żeby przepiąć pozycje fix.")


def handle_delete_unused_companies(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    companies = services.action_bus.execute(
        action=DeleteUnusedCompaniesCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            apply=args.apply,
        ),
        handler=services.delete_unused_companies,
    )

    print(f"{'NIP':<16} {'ROLA':<10} {'AKTYWNA':<8} NAZWA")
    for company in sorted(companies, key=lambda c: c.name.lower()):
        print(f"{company.tax_number:<16} {company.role.value:<10} {'tak' if company.is_active else 'nie':<8} {company.name}")

    print(f"----- Nieużywanych firm: {len(companies)} -----")
    if args.apply:
        print("Usunięto.")
    else:
        print("Tryb podglądu – nic nie usunięto. Uruchom z --apply, żeby usunąć.")


def handle_repair_orphan_documents(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    fixes = services.action_bus.execute(
        action=RepairOrphanDocumentsCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            apply=args.apply,
        ),
        handler=services.repair_orphan_documents,
    )

    for fix in fixes:
        print(f"{fix.document_number or '—':<30} {fix.old_path}")
        if fix.file_missing:
            print(f"{'':<30} BRAK PLIKU – zmieniony tylko status")
        elif fix.new_path:
            print(f"{'':<30} -> {fix.new_path}")

    print(f"----- Dokumentów APPLIED bez rekordu: {len(fixes)} -----")
    if args.apply:
        print("Przywrócono do READY – można je znów przypisać.")
    else:
        print("Tryb podglądu – nic nie zapisano. Uruchom z --apply, żeby naprawić.")
