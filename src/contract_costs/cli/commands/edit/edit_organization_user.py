from contract_costs.cli.context import get_services
from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.schemas.organization_user_role import ORG_USER_ROLE_FIELDS
from contract_costs.cli.schemas.organization_user_select import ORG_USER_SELECT_FIELDS
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.identity.change.dto.change_organization_user_role_command import \
    ChangeOrganizationUserRoleCommand
from contract_costs.services.identity.deactivate.dto.deactivate_organization_user_command import \
    DeactivateOrganizationUserCommand


def build_edit_organization_user(subparsers):
    p = subparsers.add_parser(
        "organization-user",
        help="Edit organization user",
    )
    p.add_argument("--change-role", action="store_true")
    p.add_argument("--deactivate", action="store_true")
    p.add_argument("--login", help="User login")
    p.set_defaults(handler=handle_edit_organization_user)


REGISTRY.register_group("edit", build_edit_organization_user)

def handle_edit_organization_user(args):
    if args.change_role and args.deactivate:
        print("Cannot change role and deactivate at the same time")
        return

    if args.change_role:
        _handle_change_role(args)
    elif args.deactivate:
        _handle_deactivate(args)
    else:
        print("Nothing to do. Use --change-role or --deactivate.")



def _handle_change_role(args):
    services = get_services()
    ctx = services.context

    try:
        organization_id = ctx.current_organization_id()
        actor_user_id = ctx.current_user_id()
    except ContextError as e:
        print(f"❌ {e}")
        return

    data = interactive_prompt(ORG_USER_ROLE_FIELDS)

    user = services.user_repository.get_by_login(data["login"])
    if not user:
        print("User not found")
        return

    print(
        f"\nChange role of '{data['login']}' to {data['new_role'].value}"
    )
    confirm = input("Confirm? (y/n): ").lower()
    if confirm != "y":
        print("Cancelled")
        return

    cmd = ChangeOrganizationUserRoleCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        target_user_id=user.id,
        new_role=data["new_role"],
    )

    services.change_organization_user_role.execute(cmd)
    print("User role updated")



def _handle_deactivate(args):
    services = get_services()
    ctx = services.context

    try:
        organization_id = ctx.current_organization_id()
        actor_user_id = ctx.current_user_id()
    except ContextError as e:
        print(f"❌ {e}")
        return

    data = interactive_prompt(ORG_USER_SELECT_FIELDS)

    user = services.user_repository.get_by_login(data["login"])
    if not user:
        print("User not found")
        return

    print(f"\nDeactivate user '{data['login']}'")
    confirm = input("Confirm? (y/n): ").lower()
    if confirm != "y":
        print("Cancelled")
        return

    cmd = DeactivateOrganizationUserCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        target_user_id=user.id,
    )

    services.deactivate_organization_user.execute(cmd)
    print("User deactivated")