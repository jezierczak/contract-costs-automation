# contract_costs/cli/identity/add_user.py
from contract_costs.cli.context import get_services
from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.schemas.users import USER_FIELDS
from contract_costs.cli.utils.context_helpers import require_user_id, require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.identity.add.dto.create_user_command import CreateUserCommand
from contract_costs.services.identity.exceptions import UserAlreadyExists


def build_add_user(subparsers):
    p = subparsers.add_parser(
        "user",
        help="Add user",
    )
    p.set_defaults(handler=handle_add_user)


REGISTRY.register_group("add", build_add_user)


def handle_add_user(args):
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        current_user_id = require_user_id(services.context)
    except ContextError:
        return

    data = interactive_prompt(USER_FIELDS)

    print("\nCreate user:")
    for k, v in data.items():
        print(f"  {k}: {v}")

    confirm = input("\nConfirm? (y/n): ").lower()
    if confirm != "y":
        print("Cancelled")
        return

    # created_by_user_id = None

    # TODO: Remove organization_id from CreateUserCommand (system-level action)
    #TODO usunąć org id z tego command i zmienic zachowanie permission dla akcji bez org id
    cmd = CreateUserCommand(
        login=data["login"],
        email=data.get("email"),
        full_name=data.get("full_name"),
        # created_by_user_id=current_user_id,
        actor_user_id=current_user_id,
        organization_id=organization_id,
    )
    try:
        user_id = services.action_bus.execute(action=cmd,handler=services.create_user)
    except UserAlreadyExists as e:
        print(f"❌ {e}")
        return

    print("✅ User created")
    print(f"ID: {user_id}")
    # print(f"Login: {user.login}")
