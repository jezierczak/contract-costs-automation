from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.identity.use.dto.use_organization_command import UseOrganizationCommand


def build_use_organization(subparsers):
    p = subparsers.add_parser("organization", help="Select active organization")
    p.add_argument("code", help="Organization code")
    p.set_defaults(handler=handle_use_organization)

REGISTRY.register_group("use", build_use_organization)


def handle_use_organization(args):
    services = get_services()
    try:
        user_id = require_user_id(services.context)
    except ContextError:
        return
    cmd = UseOrganizationCommand(
        actor_user_id=user_id,
        organization_code=args.code,
    )

    services.action_bus.execute(
        action=UseOrganizationCommand(
            actor_user_id=user_id,
            organization_code=args.code,
        ),
        handler=services.use_organization,
    )

    print(f"Active organization set to: {args.code}")
