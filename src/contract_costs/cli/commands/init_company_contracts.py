from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError


def build_system_commands(subparsers):
    p = subparsers.add_parser(
        "backfill",
        help="Ensure system contracts exist for OWN companies",
    )

    p.set_defaults(handler=handle_system_backfill)


REGISTRY.register_group("system", build_system_commands)


def handle_system_backfill(args):

    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    services.backfill_system_contracts.execute(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
    )

    print(f"System contracts ensured for organization {organization_id}")
