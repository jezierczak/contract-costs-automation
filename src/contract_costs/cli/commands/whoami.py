from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_user_id, require_organization_id
from contract_costs.common.context.exceptions import ContextError


def handle_whoami(args):
    services = get_services()
    try:
        user_id = require_user_id(services.context)
        organization_id = require_organization_id(services.context)
    except ContextError:
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
