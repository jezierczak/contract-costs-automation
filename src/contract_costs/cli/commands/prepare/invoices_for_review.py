import logging

from contract_costs.cli.context import get_services
from contract_costs.model.invoice import PaymentStatus, InvoiceStatus
from contract_costs.services.invoices.excel.invoice_excel_path_resolver import InvoiceExcelPathResolver
from contract_costs.services.invoices.excel.layouts.invoice_excel_layout_resolver import InvoiceExcelView
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery

logger = logging.getLogger(__name__)

def build_prepare_invoices_for_review(subparsers):
    p = subparsers.add_parser(
        "for-review",
        help="Prepare invoices, for review",
    )

    p.add_argument("--buyer-nip", help="Filter by buyer NIP")
    p.add_argument("--buyer-name", help="Filter by buyer Name")
    p.add_argument("--buyer-role", help="Filter by buyer Role")
    p.add_argument("--buyer", help="Filter by buyer")

    p.add_argument("--seller-nip", help="Filter by seller NIP")
    p.add_argument("--seller-name", help="Filter by seller Name")
    p.add_argument("--seller-role", help="Filter by seller Role")
    p.add_argument("--seller", help="Filter by seller")

    p.add_argument(
        "--status",
        nargs="+",
        choices=["NEW", "IN_PROGRESS", "PROCESSED", "DELETED"],
        help="Filter by invoice status",
    )
    p.add_argument(
        "--unpaid",
        action="store_true",
        help="Show only unpaid invoices",
    )

    p.add_argument("--from", dest="from_date")
    p.add_argument("--to", dest="to_date")

    p.add_argument(
        "--only-processed",
        action="store_true",
        help="Include only processed invoices",
    )

    p.set_defaults(handler=handle_prepare_invoices_for_review)


def handle_prepare_invoices_for_review(args) -> None:
    services = get_services()

    statuses = [InvoiceStatus[s] for s in args.status] if args.status else None

    buyer_query = InvoiceReviewQuery.build_company_query(
        any=args.buyer,
        tax_numbers=args.buyer_nip,
        name=args.buyer_name,
        role=args.buyer_role
    )
    seller_query = InvoiceReviewQuery.build_company_query(
        any=args.seller,
        tax_numbers=args.seller_nip,
        name=args.seller_name,
        role=args.seller_role
    )

    review_query = InvoiceReviewQuery(
        buyer_query=buyer_query,
        seller_query=seller_query,
        statuses=statuses,
        payment_statuses=[PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID,
                          PaymentStatus.UNKNOWN] if args.unpaid else None,
        from_date=args.from_date,
        to_date=args.to_date,
    )

    view = InvoiceExcelView.REVIEW

    output_path = InvoiceExcelPathResolver.resolve(
        view=view,
        query=review_query,
    )

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

    logger.info("Prepared invoices for review: %s", output_path)
    print(f"Prepared invoices for review :\n{output_path}")
