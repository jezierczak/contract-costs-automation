import logging
from decimal import Decimal

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.model.invoice import InvoiceStatus, PaymentStatus
from contract_costs.services.invoices.review.dto.invoice_review_query import InvoiceReviewQuery, CompanyReviewQuery

logger = logging.getLogger(__name__)


def build_show_invoices(subparsers):
    p = subparsers.add_parser(
        "invoices",
        help="Show invoices",
    )
    p.add_argument("--buyer-nip",
                   nargs="+",
                   help="Filter by buyer NIP")
    p.add_argument("--buyer-name",
                   nargs="+",
                   help="Filter by buyer Name")
    p.add_argument("--buyer-role",
                   nargs="+",
                   help="Filter by buyer Role")
    p.add_argument("--buyer", help="Filter by buyer")

    p.add_argument("--seller-nip",
                   nargs="+",
                   help="Filter by seller NIP(s)")
    p.add_argument("--seller-name",
                   nargs="+",
                   help="Filter by seller Name")

    p.add_argument("--seller-role",
                   nargs="+",
                   help="Filter by seller Role")
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
        "--last",
        type=int,
        help="Show last N invoices",
    )

    p.set_defaults(handler=handle_show_invoices)


def handle_show_invoices(args) -> None:
    services = get_services()

    # ==========================================================
    # 🔹 BRANCH: raport po NIP sprzedawcy
    # ==========================================================
    # if args.seller_nip:
    #     summary = services.invoice_seller_summary_query_service.get_by_seller_nip(
    #         args.seller_nip
    #     )
    #
    #     _print_seller_invoice_summary(summary)
    #     return

    # ==========================================================
    # 🔹 DEFAULT: lista faktur (to co masz teraz)
    # ==========================================================
    query_service = services.review_query_service

    statuses = [InvoiceStatus[s] for s in args.status] if args.status else None

    buyer_query=InvoiceReviewQuery.build_company_query(
        any=args.buyer,
        tax_numbers = args.buyer_nip,
        name = args.buyer_name,
        role = args.buyer_role
    )
    seller_query = InvoiceReviewQuery.build_company_query(
        any=args.seller,
        tax_numbers = args.seller_nip,
        name = args.seller_name,
        role = args.seller_role
    )

    review_query = InvoiceReviewQuery(
        buyer_query=buyer_query,
        seller_query=seller_query,
        statuses=statuses,
        payment_statuses = [PaymentStatus.UNPAID, PaymentStatus.PARTIALLY_PAID, PaymentStatus.UNKNOWN] if args.unpaid else None,
        from_date=args.from_date,
        to_date=args.to_date,
    )
    print("Preparing invoices... ")
    if review_query.statuses:
        print(f"Statuses in: {[status.name for status in review_query.statuses]}")
    if review_query.payment_statuses:
        print(f"Payment statuses in: {[p.name for p in review_query.payment_statuses]}")
    if review_query.from_date:
        print(f"From date: {review_query.from_date}")
    if review_query.to_date:
        print(f"To date: {review_query.to_date}")
    if args.last:
        print(f"Last {args.last} invoices")
    print("=" * 192)

    result_invoices = query_service.list_for_review(review_query)
    if not result_invoices:
        print("No invoices found.")
        return

    if args.last:
        result_invoices = result_invoices[:args.last]

    print(
        f"{fmt("NUMER FAKTURY", 50)} "
      
        f"{fmt("DATA FAKT.", 10)} "
        f"{fmt("NABYWCA", 10)} "
        f"{fmt("SPRZEDAWCA", 10)} "
        f"{fmt("NETTO", 10)} "
        f"{fmt("VAT", 10)} "
        f"{fmt("BRUTTO", 10)} "
        f"{fmt("NIEOPOD.", 10)} "
        f"{fmt("METODA PŁ.", 15)} "
        f"{fmt("STATUS PŁ.", 10)} "
        f"{fmt("ZAPŁ. DO", 12)}"
        f"{fmt("STATUS", 18)} "
        f"{fmt("DIRECTION", 10)} "
        f"{fmt("CONTRACTS", 18)} "
    )
    NET: Decimal = Decimal("0.00")
    VAT: Decimal = Decimal("0.00")
    GROSS: Decimal = Decimal("0.00")
    NOT_EVIDENCE: Decimal = Decimal("0.00")
    for inv in result_invoices:
        # inv = invoice_details_service.get_invoice(i.id)
        print(
            f"{fmt(inv.invoice_number, 50)} "
            
            f"{fmt(inv.invoice_date, 10)} "
            f"{fmt(inv.buyer_tax_number, 10)} "
            f"{fmt(inv.seller_tax_number, 10)} "
            f"{fmt(inv.total_net, 10)} "
            f"{fmt(inv.total_vat, 10)} "
            f"{fmt(inv.total_gross, 10)} "
            f"{fmt(inv.total_not_evidenced, 10)} "
            f"{fmt(inv.payment_method, 15)} "
            f"{fmt(inv.payment_status, 10)} "
            f"{fmt(inv.due_date, 12)}"
            f"{fmt(inv.status, 18)} "
            f"{fmt(inv.direction, 10)} "
            f"{fmt(inv.contract_codes, 18)} "
        )
        NET += inv.total_net
        VAT += inv.total_vat
        GROSS+=inv.total_gross
        NOT_EVIDENCE+=inv.total_not_evidenced

    print("-" * 192)
    print(  f"{fmt("SUMA", 98)} "
            f"{fmt(NET, 10)} "
            f"{fmt(VAT, 10)} "
            f"{fmt(GROSS, 10)} "
            f"{fmt(NOT_EVIDENCE, 10)} ")

def fmt(value, width: int) -> str:
    if value is None:
        return "-".ljust(width)
    return str(value).ljust(width)

def _print_seller_invoice_summary(summary):
    print("=" * 100)
    print(f"SELLER: {summary.seller_name}")
    print(f"NIP:    {summary.seller_tax_number}")
    print("=" * 100)

    print(
        f"{'INVOICE':<20} {'DATE':<12} {'STATUS':<10} "
        f"{'NET':>10} {'VAT':>10} {'GROSS':>10} {'PAID':>6}"
    )
    print("-" * 100)

    for r in summary.invoices:
        print(
            f"{r.invoice_number:<20} "
            f"{r.invoice_date or '-':<12} "
            f"{r.status.name:<10} "
            f"{r.net:>10.2f} "
            f"{r.vat:>10.2f} "
            f"{r.gross:>10.2f} "
            f"{'YES' if r.paid else 'NO':>6}"
        )

    print("-" * 100)
    print(
        f"{'TOTAL':<44} "
        f"{summary.total_net:>10.2f} "
        f"{summary.total_vat:>10.2f} "
        f"{summary.total_gross:>10.2f}"
    )

REGISTRY.register_group("show", build_show_invoices)
