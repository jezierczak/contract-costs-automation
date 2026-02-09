from contract_costs.cli.context import get_services
from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.schemas.organization_users import ORG_USER_FIELDS
from contract_costs.cli.utils.context_helpers import require_user_id, require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.identity.add.dto.assign_user_to_organization_command import AssignUserToOrganizationCommand


def build_add_organization_user(subparsers):
    p = subparsers.add_parser(
        "organization-user",
        help="Add user to organization",
    )
    p.set_defaults(handler=handle_add_organization_user)

REGISTRY.register_group("add", build_add_organization_user)


def handle_add_organization_user(args):
    services = get_services()

    try:
        current_user_id = require_user_id(services.context)
        org_id = require_organization_id(services.context)
    except ContextError:
        return

    data = interactive_prompt(ORG_USER_FIELDS)

    print("\nAdd user to organization:")
    for k, v in data.items():
        print(f"  {k}: {v}")

    confirm = input("\nConfirm? (y/n): ").lower()
    if confirm != "y":
        print("Cancelled")
        return

    user = services.user_repository.get_by_login(data["login"])
    if not user:
        print("User not found")
        return

    cmd = AssignUserToOrganizationCommand(
        organization_id=org_id,
        actor_user_id=current_user_id,
        target_user_id=user.id,
        role=data["role"],
    )

    services.add_organization_user.execute(cmd)

    print("User added to organization")
