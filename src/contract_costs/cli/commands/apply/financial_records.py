import logging
from pathlib import Path

from contract_costs.cli.commands.apply.financial_records_paid import build_apply_financial_records_paid
from contract_costs.cli.commands.apply.financial_records_to_accountant import build_apply_financial_records_to_accountant
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_user_id, require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import FinancialRecordInvoiceAssignmentFileManager
from contract_costs.services.financial_records.assigment.apply.commands.apply_invoice_excel_bach_command import \
    ApplyInvoiceExcelBatchCommand

from contract_costs.services.financial_records.assigment.invoice_sources.excel.invoice_excel_loader import load_invoice_excel_batch

logger = logging.getLogger(__name__)

def build_apply_financial_records(subparsers):
    parser = subparsers.add_parser(
        "records",
        help="Apply prepared financial records (Excel import)",
    )
    invoice_sub = parser.add_subparsers(
        dest="workflow",
        required=True,
    )

    build_apply_records_to_processed(invoice_sub)
    build_apply_financial_records_to_accountant(invoice_sub)
    build_apply_financial_records_paid(invoice_sub)


def build_apply_records_to_processed(subparsers):
    parser = subparsers.add_parser(
        "to-processed",
        aliases=["ass","pro"],
        help="Apply prepared financial records (Excel import)",
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to financial records excel file",
    )

    parser.set_defaults(handler=handle_apply_financial_records)


def handle_apply_financial_records(args):

    file = args.file

    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    file_manager = FinancialRecordInvoiceAssignmentFileManager(organization_id=organization_id)

    if file is None:
        path = file_manager.get_active_file()
        managed = True
    else:
        path = Path(file)
        managed = False

    batch = load_invoice_excel_batch(path)

    cmd = ApplyInvoiceExcelBatchCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        batch=batch,
    )

    services.action_bus.execute(
        action=cmd,
        handler=services.apply_financial_record_excel_batch,
    )

    if managed:
        file_manager.mark_processed()
    logger.info(f"Invoices applied from: {path}")


REGISTRY.register_group("apply", build_apply_financial_records)

