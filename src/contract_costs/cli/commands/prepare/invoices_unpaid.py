import logging

from contract_costs.cli.context import get_services
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InvoiceExcelPrepareFileManager
from contract_costs.model.invoice import PaymentStatus, InvoiceStatus

from contract_costs.services.invoices.excel.layouts.invoice_excel_layout_resolver import InvoiceExcelView
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery

logger = logging.getLogger(__name__)

def build_prepare_invoices_unpaid(subparsers):
    p = subparsers.add_parser(
        "unpaid",
        aliases=["unp"],
        help="Prepare unpaid invoices, to assign paid",
    )

    p.add_argument("--from", dest="from_date")
    p.add_argument("--to", dest="to_date")

    p.add_argument(
        "--only-processed",
        action="store_true",
        help="Include only processed invoices",
    )

    p.set_defaults(handler=handle_prepare_invoices_unpaid)




def handle_prepare_invoices_unpaid(args) -> None:
    services = get_services()

    review_query = InvoiceReviewQuery(
        statuses=[InvoiceStatus.PROCESSED, InvoiceStatus.SENT_TO_ACCOUNTANT],
        payment_statuses = [PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID, PaymentStatus.UNKNOWN],
        from_date=args.from_date,
        to_date=args.to_date,
    )

    view = InvoiceExcelView.UNPAID
    file_manager = InvoiceExcelPrepareFileManager(
        view=view,
        query=review_query,
    )
    output_path = file_manager.prepare_target()

    services.invoice_excel_export_service.export(
        review_query=review_query,
        view=view,
        output_path=output_path,
    )

    logger.info("Prepared unpaid invoices for assignment: %s", output_path)
    print(f"Prepared invoices for assignment :\n{output_path}")
