from contract_costs.cli.context import get_services
from contract_costs.cli.printers.cost_type_printer import CostTypePrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.services.cost_types.query.dto.cost_type_query import CostTypeQuery


def build_show_cost_types(subparsers):
    p = subparsers.add_parser(
        "cost-types",
        help="Show cost types",
    )

    p.add_argument("--code", help="Filter by code")
    p.add_argument("--inactive", action="store_true")
    p.add_argument("--search", help="Search in name / description")

    p.set_defaults(handler=handle_show_cost_types)


REGISTRY.register_group("show", build_show_cost_types)


def handle_show_cost_types(args):
    services = get_services()

    query = CostTypeQuery(
        code=args.code,
        include_inactive=args.inactive,
        search=args.search,
    )

    items = services.cost_type_query_service.list(query)

    CostTypePrinter.print(items)
