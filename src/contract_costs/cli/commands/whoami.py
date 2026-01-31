from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.common.context.exceptions import ContextError


def handle_whoami(args):
    services = get_services()
    try:
        user_id = services.context.current_user_id()
        organization_id = services.context.current_organization_id()
    except ContextError as e:
        print(f"❌ {e}")
        return
    user = services.user_repository.get(user_id)
    organization = services.organization_repository.get(organization_id)

    if not user:
        print("User not found (corrupted session?)")
        return

    print(f"{user.login} ({user.full_name})")
    if not organization:
        print("Organization not found for this user")
    else:
        print(f"{organization.code} ({organization.name})")

REGISTRY.register_simple("whoami;Checks logged in user identity", handle_whoami)
