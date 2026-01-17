import logging
from pathlib import Path

from contract_costs.cli.commands.apply.invoices_paid import build_apply_invoices_paid
from contract_costs.cli.commands.apply.invoices_to_accountant import build_apply_invoices_to_accountant
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InputsInvoiceAssignmentFileManager

from contract_costs.services.invoices.assigment.invoice_sources.excel.invoice_excel_loader import load_invoice_excel_batch

logger = logging.getLogger(__name__)

def build_apply_invoices(subparsers):
    parser = subparsers.add_parser(
        "invoices",
        help="Apply prepared invoices (Excel import)",
    )
    invoice_sub = parser.add_subparsers(
        dest="workflow",
        required=True,
    )

    build_apply_invoices_to_processed(invoice_sub)
    build_apply_invoices_to_accountant(invoice_sub)
    build_apply_invoices_paid(invoice_sub)


def build_apply_invoices_to_processed(subparsers):
    parser = subparsers.add_parser(
        "to-processed",
        aliases=["ass","pro"],
        help="Apply prepared invoices (Excel import)",
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to invoices excel file",
    )

    parser.set_defaults(handler=handle_apply_invoices)


def handle_apply_invoices(args):

    file = args.file

    services = get_services()
    file_manager = InputsInvoiceAssignmentFileManager()

    if file is None:
        path = file_manager.get_active_file()
        managed = True
    else:
        path = Path(file)
        managed = False

    # excel_path = Path(path)

    batch = load_invoice_excel_batch(path)

    service = services.apply_invoice_excel_batch
    service.apply(batch)

    if managed:
        file_manager.mark_processed()
    logger.info(f"Invoices applied from: {path}")


REGISTRY.register_group("apply", build_apply_invoices)
