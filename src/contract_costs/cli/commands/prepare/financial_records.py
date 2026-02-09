import logging

from contract_costs.cli.commands.prepare.financial_records_for_accountant import build_prepare_financial_records_for_accountant
from contract_costs.cli.commands.prepare.financial_records_for_review import build_prepare_financial_records_for_review
from contract_costs.cli.commands.prepare.financial_records_unpaid import build_prepare_financial_records_unpaid
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import FinancialRecordInvoiceAssignmentFileManager
from contract_costs.model.financial_record import FinancialRecordStatus

logger = logging.getLogger(__name__)


# =========================================================
# Builder (argparse)
# =========================================================


def build_prepare_financial_records(subparsers):
    p = subparsers.add_parser(
        "records",
        help="Prepare financial records workflows",
    )

    invoice_sub = p.add_subparsers(
        dest="workflow",
        required=True,
    )

    build_prepare_financial_records_for_assignment(invoice_sub)
    build_prepare_financial_records_for_accountant(invoice_sub)
    build_prepare_financial_records_unpaid(invoice_sub)
    build_prepare_financial_records_for_review(invoice_sub)

def build_prepare_financial_records_for_assignment(subparsers):
    """
    prepare invoices

    Generates Excel with invoices prepared for editing.
    """
    p = subparsers.add_parser(
        "for-assignment",
        aliases=["ass"],
        help="Prepare financial records for assignment/editing",
    )

    p.add_argument(
        "mode",
        nargs="?",
        choices=["new_cost","new_revenue","draft", "in_progress", "open"],
        default="open",
        help="Financial record status filter (default: open)",
    )

    p.add_argument(
        "--contract",
        help="Filter by contract code or UUID (optional)",
    )

    # p.add_argument(
    #     "--excel",
    #     action="store_true",
    #     help="Generate Excel output (default behavior)",
    # )

    p.set_defaults(handler=handle_prepare_financial_records)


# =========================================================
# Handler
# =========================================================

def handle_prepare_financial_records(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    statuses = {
        "new_cost": [FinancialRecordStatus.NEW_COST],
        "draft": [FinancialRecordStatus.DRAFT],
        "new_revenue": [FinancialRecordStatus.NEW_REVENUE],
        "in_progress": [FinancialRecordStatus.IN_PROGRESS],
        "open": [FinancialRecordStatus.NEW_COST, FinancialRecordStatus.DRAFT, FinancialRecordStatus.NEW_REVENUE, FinancialRecordStatus.IN_PROGRESS],
    }[args.mode if args.mode else "open"]

    file_manager = FinancialRecordInvoiceAssignmentFileManager(organization_id=organization_id)
    output_path = file_manager.prepare_target()

    bundle = services.generate_financial_record_assignment_bundle.execute(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        invoice_status=statuses,
        # contract_ref=args.contract,
    )
    services.export_financial_record_assignment_excel_service.execute(
        organization_id=organization_id,
        bundle=bundle,
        output_path=output_path )

    logger.info(
        "Financial records prepared for assignment (org=%s): %s",
        organization_id,
        output_path,
    )


# =========================================================
# Registry registration
# =========================================================

REGISTRY.register_group("prepare", build_prepare_financial_records)
