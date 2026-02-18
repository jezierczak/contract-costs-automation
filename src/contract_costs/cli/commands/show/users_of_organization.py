from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_user_id, require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.identity.query.dto.list_organization_users_query import ListOrganizationUsersQuery


def build_show_organizations(subparsers):
    p = subparsers.add_parser("organizations", help="Show organizations")
    p.set_defaults(handler=handle_show_organization_users)

REGISTRY.register_group("show", build_show_organizations)


def handle_show_organization_users(args=None):
    services = get_services()

    try:
        org_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    items = services.action_bus.execute(
        action=ListOrganizationUsersQuery(
            organization_id=org_id,
            actor_user_id=actor_user_id,
        ),
        handler=services.list_organization_users_query_service,
    )

    if not items:
        print("No users found in organization.")
        return

    print("\nOrganization users:\n")
    for u in items:
        status = "ACTIVE" if u.is_active else "INACTIVE"
        print(
            f"{u.login:<15} {u.full_name:<30} "
            f"[{u.role:<6}] {status}"
        )