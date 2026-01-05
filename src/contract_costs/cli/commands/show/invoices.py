import logging
from decimal import Decimal

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.model.invoice import InvoiceStatus, PaymentStatus

logger = logging.getLogger(__name__)


def build_show_invoices(subparsers):
    p = subparsers.add_parser(
        "invoices",
        help="Show invoices",
    )
    p.add_argument("--seller-nip", help="Filter by seller NIP")
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
    if args.seller_nip:
        summary = services.invoice_seller_summary_query_service.get_by_seller_nip(
            args.seller_nip
        )

        _print_seller_invoice_summary(summary)
        return

    # ==========================================================
    # 🔹 DEFAULT: lista faktur (to co masz teraz)
    # ==========================================================

    inv_repo = services.invoice_repository


    invoice_details_service = services.invoice_query_service
    statuses = [InvoiceStatus[s] for s in args.status] if args.status else None
    invoices = inv_repo.list_invoices()
    invoices = sorted(invoices, key=lambda x: x.timestamp, reverse=True)
    # companies = comp_repo.list_companies()
    # lines = line_repo.list_lines()
    if args.unpaid:
        invoices = [i for i in invoices if i.payment_status == PaymentStatus.UNPAID]

    if statuses:
        invoices = [i for i in invoices if i.status in statuses]
    if args.last:
        invoices = invoices[:args.last]


    if not invoices:
        print("No invoices found.")
        return

    print(
        f"{fmt("NUMER FAKTURY", 65)} "
        f"{fmt("STATUS", 10)} "
        f"{fmt("DATA FAKT.", 10)} "
        f"{fmt("NABYWCA", 10)} "
        f"{fmt("SPRZEDAWCA", 10)} "
        f"{fmt("NETTO", 10)} "
        f"{fmt("VAT", 10)} "
        f"{fmt("BRUTTO", 10)} "
        f"{fmt("NIEOPOD.", 10)} "
        f"{fmt("METODA PŁ.", 15)} "
        f"{fmt("STATUS PŁ.", 10)} "
        f"{fmt("ZAPŁ. DO", 10)}"
    )
    NET: Decimal = Decimal("0.00")
    VAT: Decimal = Decimal("0.00")
    GROSS: Decimal = Decimal("0.00")
    NOT_EVIDENCE: Decimal = Decimal("0.00")
    for i in invoices:
        inv = invoice_details_service.get_by_invoice_number(i.invoice_number)
        print(
            f"{fmt(inv.invoice_number, 65)} "
            f"{fmt(inv.status, 10)} "
            f"{fmt(inv.invoice_date, 10)} "
            f"{fmt(inv.buyer_tax_number, 10)} "
            f"{fmt(inv.seller_tax_number, 10)} "
            f"{fmt(inv.total_net, 10)} "
            f"{fmt(inv.total_vat, 10)} "
            f"{fmt(inv.total_gross, 10)} "
            f"{fmt(inv.total_not_evidenced, 10)} "
            f"{fmt(inv.payment_method, 15)} "
            f"{fmt(inv.payment_status, 10)} "
            f"{fmt(inv.due_date, 10)}"
        )
        NET += inv.total_net
        VAT += inv.total_vat
        GROSS+=inv.total_gross
        NOT_EVIDENCE+=inv.total_not_evidenced

    print(  f"{fmt("SUMA", 109)} "
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
