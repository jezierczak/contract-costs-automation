from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.common.context.exceptions import ContextError


def build_show_organizations(subparsers):
    p = subparsers.add_parser("organizations", help="Show organizations")
    p.set_defaults(handler=handle_show_organizations)

REGISTRY.register_group("show", build_show_organizations)


def handle_show_organizations(args=None):
    services = get_services()

    # 🔴 tymczasowo – do czasu auth
    try:
        user_id = services.context.current_user_id()
    except ContextError as e:
        print(f"❌ {e}")
        return

    items = services.show_organizations.list_for_user(user_id=user_id)

    if not items:
        print("No organizations found.")
        return

    print("\nOrganizations:\n")
    for o in items:
        status = "ACTIVE" if o.is_active else "INACTIVE"
        print(
            f"{o.code:<15} {o.name:<40} "
            f"[{o.role:<6}] {status}"
        )
