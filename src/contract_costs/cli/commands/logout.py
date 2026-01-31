from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.session import  clear_session


def handle_logout(args):
    clear_session()
    print("Logged out")

REGISTRY.register_simple("logout;Logouts active user", handle_logout)
