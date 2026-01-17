import logging

from contract_costs.cli.context import get_services
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InvoiceExcelPrepareFileManager
# from contract_costs.services.invoices.excel.invoice_excel_path_resolver import InvoiceExcelPathResolver
from contract_costs.services.invoices.excel.layouts.invoice_excel_layout_resolver import InvoiceExcelView
from contract_costs.services.invoices.review.invoice_review_list_query_service import InvoiceReviewQuery

logger = logging.getLogger(__name__)

def build_prepare_invoices_for_accountant(subparsers):
    p = subparsers.add_parser(
        "for-accountant",
        aliases=["acc"],
        help="Prepare invoices for sending to accountant",
    )

    p.add_argument("--from", dest="from_date")
    p.add_argument("--to", dest="to_date")

    p.add_argument(
        "--include-unprocessed",
        dest="include_unprocessed",
        action="store_true",
        help="Include invoices not yet processed",
    )

    p.set_defaults(handler=handle_prepare_invoices_for_accountant)


def handle_prepare_invoices_for_accountant(args) -> None:
    services = get_services()

    review_query = InvoiceReviewQuery(
        from_date=args.from_date,
        to_date=args.to_date,
        only_ready_for_accountant=not args.include_unprocessed,
    )

    view = InvoiceExcelView.FOR_ACCOUNTANT

    file_manager = InvoiceExcelPrepareFileManager(
        view=view,
        query=review_query,
    )
    output_path = file_manager.prepare_target()
    # output_path = InvoiceExcelPathResolver.resolve(
    #     view=view,
    #     query=review_query,
    # )
    #
    # if output_path.exists():
    #     raise RuntimeError(
    #         f"Excel already exists: {output_path}\n"
    #         "Apply or remove it before preparing again."
    #     )

    services.invoice_excel_export_service.export(
        review_query=review_query,
        view=view,
        output_path=output_path,
    )

    logger.info("Prepared invoices for accountant: %s", output_path)
    print(f"Prepared invoices for accountant:\n{output_path}")
