import logging
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY

logger = logging.getLogger(__name__)



def build_show_invoice(subparsers):
    p = subparsers.add_parser(
        "invoice",
        help="Show single invoice with lines",
    )

    p.add_argument(
        "number",
        help="Invoice number",
    )

    p.set_defaults(handler=handle_show_invoice)

REGISTRY.register_group("show", build_show_invoice)


def handle_show_invoice(args) -> None:
    services = get_services()
    invoice_details_service = services.invoice_query_service

    invoice = invoice_details_service.get_by_invoice_number(args.number)

    if not invoice:
        print(f"Invoice not found: {args.number}")
        return

    _print_invoice_header(invoice)
    _print_invoice_lines(invoice)


def fmt(val, width):
    return str(val if val is not None else "-").ljust(width)

def _print_invoice_header(inv):
    print("=" * 120)
    print(f"INVOICE: {inv.invoice_number}")
    print("-" * 120)

    print(f"Status:          {inv.status}")
    print(f"Invoice date:    {inv.invoice_date}")
    print(f"Selling date:    {inv.selling_date}")
    print(f"Due date:        {inv.due_date}")
    print(f"Payment method:  {inv.payment_method}")
    print(f"Payment status:  {inv.payment_status}")
    print()

    print("BUYER:")
    print(f"  Name: {inv.buyer_name}")
    print(f"  NIP:  {inv.buyer_tax_number}")
    print()

    print("SELLER:")
    print(f"  Name: {inv.seller_name}")
    print(f"  NIP:  {inv.seller_tax_number}")
    print()

    print("TOTALS:")
    print(f"  Net:           {inv.total_net}")
    print(f"  VAT:           {inv.total_vat}")
    print(f"  Gross:         {inv.total_gross}")
    print(f"  Not evidenced: {inv.total_not_evidenced}")
    print("=" * 120)



def _print_invoice_lines(inv):
    if not inv.lines:
        print("No invoice lines.")
        return

    print()
    print("INVOICE LINES:")
    print(
        f"{fmt('Item', 40)} "
        f"{fmt('Qty', 6)} "
        f"{fmt('Unit', 6)} "
        f"{fmt('Net', 10)} "
        f"{fmt('VAT', 6)} "
        f"{fmt('Gross', 10)} "
        f"{fmt('Contract', 12)} "
        f"{fmt('Cost node', 12)}"
    )

    print("-" * 120)

    for l in inv.lines:


        print(
            f"{fmt(l.item_name, 40)} "
            f"{fmt(l.quantity, 6)} "
            f"{fmt(l.unit, 6)} "
            f"{fmt(l.net, 10)} "
            f"{fmt(l.vat, 6)} "
            f"{fmt(l.gross, 10)} "
            f"{fmt(l.contract_code, 12)} "
            f"{fmt(l.cost_node_code, 12)}"
        )
