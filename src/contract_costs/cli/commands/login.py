from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.session import save_session


def build_login(p):
    p.add_argument("login", help="user login")
    p.set_defaults(handler=handle_login)

REGISTRY.register_simple_builder("login", build_login)


def handle_login(args):
    services = get_services()

    user = services.user_repository.get_by_login(args.login)
    if not user or not user.is_active:
        print("Invalid user")
        return

    # ⛔ hasło – NIE TERAZ
    save_session(user_id=user.id)

    print(f"Logged in as {user.login}")

