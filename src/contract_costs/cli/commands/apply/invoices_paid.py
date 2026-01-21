import logging

from contract_costs.cli.context import get_services
from contract_costs.infrastructure.excel.invoice_excel_context import InvoiceExcelContext
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InvoiceExcelPrepareFileManager
from contract_costs.model.invoice import InvoiceStatus, PaymentStatus
# from contract_costs.services.invoices.excel.invoice_excel_path_resolver import InvoiceExcelPathResolver
from contract_costs.services.invoices.excel.layouts.invoice_excel_layout_resolver import InvoiceExcelView
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery

logger = logging.getLogger(__name__)

def build_apply_invoices_paid(subparsers):
    parser = subparsers.add_parser(
        "paid",
        aliases=["unp"],
        help="Apply invoices paid",
    )

    parser.set_defaults(handler=handle_apply_invoices_paid)

def handle_apply_invoices_paid(args):
    services = get_services()

    # 🔑 TA SAMA LOGIKA CO W PREPARE
    file_manager = InvoiceExcelPrepareFileManager(
        view=InvoiceExcelView.UNPAID,
        query=InvoiceReviewQuery(
            statuses=[InvoiceStatus.PROCESSED, InvoiceStatus.SENT_TO_ACCOUNTANT],
            payment_statuses=[PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID, PaymentStatus.UNKNOWN],
        ),
    )
    path = file_manager.get_active_file()

    commands = services.invoice_action_excel_loader.load(path,context=InvoiceExcelContext.UNPAID)


    for cmd in commands:
        services.invoice_action_service.execute(cmd)

    file_manager.mark_processed()
    logger.info(
        "Invoices set paid: %d",
        len(commands),
    )

    print(f"✔ Set paid: {len(commands)} invoices")
