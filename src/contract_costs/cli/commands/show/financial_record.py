import logging
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.financial_records.queries.dto.financial_record_details_query import \
    FinancialRecordDetailsQuery

logger = logging.getLogger(__name__)



def build_show_financial_record(subparsers):
    p = subparsers.add_parser(
        "record",
        help="Show single financial record with lines",
    )

    p.add_argument(
        "number",
        help="Financial record reference",
    )

    p.set_defaults(handler=handle_show_financial_record)

REGISTRY.register_group("show", build_show_financial_record)


def handle_show_financial_record(args) -> None:
    services = get_services()
    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return


    record_details_service = services.financial_record_query_service

    # record = record_details_service.get_by_reference(
    #     organization_id=organization_id,
    #     reference=args.number)
    #
    record = services.action_bus.execute(
        action=FinancialRecordDetailsQuery(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            reference=args.number,
        ),
        handler=record_details_service,)

    if not record:
        print(f"Financial record not found: {args.number}")
        return

    _print_record_header(record)
    _print_record_lines(record)


def fmt(val, width):
    s = "-" if val is None else str(val)
    return s[:width].ljust(width)

def _print_record_header(rec):
    print("=" * 120)
    print(f"UUID: {rec.id}")
    print("-" * 120)
    print(f"RECORD: {rec.reference}")
    print("-" * 120)

    print(f"Status:          {rec.status}")
    print(f"Direction:       {rec.direction}")
    print(f"Contracts:       {rec.contract_codes}")
    print(f"Invoice date:    {rec.invoice_date}")
    print(f"Selling date:    {rec.selling_date}")
    print(f"Due date:        {rec.due_date}")
    print(f"Payment method:  {rec.payment_method}")
    print(f"Payment status:  {rec.payment_status}")
    print()

    print("BUYER:")
    print(f"  Name: {rec.buyer_name}")
    print(f"  NIP:  {rec.buyer_tax_number}")
    print()

    print("SELLER:")
    print(f"  Name: {rec.seller_name}")
    print(f"  NIP:  {rec.seller_tax_number}")
    print()

    print("TOTALS:")
    print(f"  Net:           {rec.total_net}")
    print(f"  VAT:           {rec.total_vat}")
    print(f"  Gross:         {rec.total_gross}")
    print(f"  Not evidenced: {rec.total_not_evidenced}")
    print("=" * 132)



def _print_record_lines(rec):
    if not rec.lines:
        print("No financial record lines.")
        return

    print()
    print("FINANCIAL RECORD LINES:")
    print(
        f"{fmt('Item', 40)} "
        f"{fmt('Qty', 6)} "
        f"{fmt('Unit', 6)} "
        f"{fmt('Net', 10)} "
        f"{fmt('VAT', 6)} "
        f"{fmt('Gross', 10)} "
        f"{fmt('Contract', 12)} "
        f"{fmt('Cost node', 12)}"
        f"{fmt('Cost type', 12)}"
    )

    print("-" * 132)

    for l in rec.lines:


        print(
            f"{fmt(l.item_name, 40)} "
            f"{fmt(l.quantity, 6)} "
            f"{fmt(l.unit, 6)} "
            f"{fmt(l.amount_value, 10)} "
            f"{fmt(l.vat, 6)} "
            f"{fmt(l.gross, 10)} "
            f"{fmt(l.contract_reference, 12)} "
            f"{fmt(l.cost_node_code, 12)}"
            f"{fmt(l.cost_type_code, 12)}"
        )
