from contract_costs.cli.context import get_services
from contract_costs.cli.printers.value_type_printer import ValueTypePrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.value_types.query.dto.value_type_query import ValueTypeQuery


def build_show_value_types(subparsers):
    p = subparsers.add_parser(
        "value-types",
        help="Show value types",
    )

    p.add_argument("--code", help="Filter by code")
    p.add_argument("--inactive", action="store_true")
    p.add_argument("--search", help="Search in name / description")

    p.set_defaults(handler=handle_show_value_types)


REGISTRY.register_group("show", build_show_value_types)


def handle_show_value_types(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    query = ValueTypeQuery(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        code=args.code,
        include_inactive=args.inactive,
        search=args.search,
    )

    items = services.value_type_query_service.list_contracts(query)
    items = services.action_bus.execute(
        action=query,
        handler=services.value_type_query_service
    )

    ValueTypePrinter.print(items,organization_id)
