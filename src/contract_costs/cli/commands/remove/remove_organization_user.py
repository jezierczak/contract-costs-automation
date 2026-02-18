# contract_costs/cli/identity/remove_organization_user.py
from contract_costs.cli.context import get_services
from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.schemas.organization_users_remove import ORG_USER_REMOVE_FIELDS
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.identity.remove.dto.remove_organization_user_command import (
    RemoveOrganizationUserCommand,
)


def build_remove_organization_user(subparsers):
    p = subparsers.add_parser(
        "organization-user",
        help="Remove user from organization",
    )
    p.set_defaults(handler=handle_remove_organization_user)


REGISTRY.register_group("remove", build_remove_organization_user)


def handle_remove_organization_user(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return


    data = interactive_prompt(ORG_USER_REMOVE_FIELDS)

    user = services.user_repository.get_by_login(data["login"])
    if not user:
        print("User not found")
        return

    print("\nRemove user from organization:")
    print(f"  login: {data['login']}")

    confirm = input("\nConfirm? (y/n): ").lower()
    if confirm != "y":
        print("Cancelled")
        return

    cmd = RemoveOrganizationUserCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        target_user_id=user.id,
    )
    services.action_bus.execute(action=cmd,handler=services.remove_organization_user)

    print("User removed from organization")
