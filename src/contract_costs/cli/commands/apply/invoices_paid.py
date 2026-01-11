import logging
from pathlib import Path

from contract_costs.cli.context import get_services
from contract_costs.infrastructure.excel.invoice_excel_context import InvoiceExcelContext
from contract_costs.model.invoice import InvoiceStatus, PaymentStatus
from contract_costs.services.invoices.excel.invoice_excel_path_resolver import InvoiceExcelPathResolver
from contract_costs.services.invoices.excel.layouts.invoice_excel_layout_resolver import InvoiceExcelView
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery

logger = logging.getLogger(__name__)

def build_apply_invoices_paid(subparsers):
    parser = subparsers.add_parser(
        "paid",
        help="Apply invoices paid",
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to invoices excel file",
    )

    parser.set_defaults(handler=handle_apply_invoices_paid)

def handle_apply_invoices_paid(args):
    services = get_services()
    if args.file:
        path = Path(args.file)
    else:
        # 🔑 TA SAMA LOGIKA CO W PREPARE
        path = InvoiceExcelPathResolver.resolve(
            view=InvoiceExcelView.UNPAID,
            query=InvoiceReviewQuery(
                statuses=[InvoiceStatus.PROCESSED, InvoiceStatus.SENT_TO_ACCOUNTANT],
                payment_statuses=[PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID, PaymentStatus.UNKNOWN],
            ),
        )

    if not path.exists():
        raise RuntimeError(f"Excel file not found: {path}")
    commands = services.invoice_action_excel_loader.load(path,context=InvoiceExcelContext.UNPAID)

    for cmd in commands:
        services.invoice_action_service.execute(cmd)


    logger.info(
        "Invoices sent to accountant: %d",
        len(commands),
    )

    print(f"✔ Sent to accountant: {len(commands)} invoices")
