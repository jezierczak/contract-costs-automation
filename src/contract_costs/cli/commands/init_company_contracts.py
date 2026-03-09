import logging
from dataclasses import replace

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.contracts.migration.backfill_system_contracts_command import BackfillSystemContractsCommand
from contract_costs.services.documents.scoring.simple_scoring_policy import SimpleScoringPolicy

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


REGISTRY.register_group("system", build_system_commands)


def handle_system_backfill(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = services.context.user_id
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