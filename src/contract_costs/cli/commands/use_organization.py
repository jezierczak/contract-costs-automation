from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
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
        cmd = UseOrganizationCommand(
            user_id=services.context.current_user_id(),
            organization_code=args.code,
        )
    except ContextError as e:
        print(f"❌ {e}")
        return
    services.use_organization.execute(cmd)

    print(f"Active organization set to: {args.code}")
