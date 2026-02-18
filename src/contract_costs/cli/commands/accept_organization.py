from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.identity.accept.dto.accept_organization_invite_command import (
    AcceptOrganizationInviteCommand,
)


def build_accept_organization(subparsers):
    p = subparsers.add_parser(
        "organization",
        help="Accept organization invitation",
    )
    p.set_defaults(handler=handle_accept_organization)


REGISTRY.register_group("accept", build_accept_organization)


def handle_accept_organization(args):
    services = get_services()
    ctx = services.context

    try:
        org_id = ctx.current_organization_id()
        user_id = ctx.current_user_id()
    except ContextError as e:
        print(f"❌ {e}")
        return

    cmd = AcceptOrganizationInviteCommand(
        organization_id=org_id,
        actor_user_id=user_id,
    )

    services.accept_organization_invite.execute(cmd)

    services.action_bus.execute(
        action=cmd,
        handler=services.accept_organization_invite,
    )

    print("✅ Organization invitation accepted")
