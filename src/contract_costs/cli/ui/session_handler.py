from contract_costs.cli.context import get_services
from contract_costs.common.context.exceptions import ContextError


def print_session_header() -> None:
    services = get_services()
    ctx = services.context

    print("\n----------------------------------")

    # USER
    try:
        user_id = ctx.current_user_id()
        user = services.user_repository.get(user_id)
        if user:
            print(f"👤 User: {user.login} ({user.full_name})")
        else:
            print("👤 User: <unknown>")
    except ContextError:
        print("👤 User: — not logged in —")
        print("----------------------------------")
        return

    # ORGANIZATION
    try:
        org_id = ctx.current_organization_id()
        org = services.organization_repository.get(org_id)
        if org:
            print(f"🏢 Org:  {org.code} | {org.name}")
        else:
            print("🏢 Org:  <unknown>")
    except ContextError:
        print("🏢 Org:  — not selected —")

    print("----------------------------------")
    print()