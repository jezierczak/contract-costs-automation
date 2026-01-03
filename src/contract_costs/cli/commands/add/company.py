from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.commands.add.add_company import handle_add_company

def build_add_company(subparsers):
    p = subparsers.add_parser("company", help="Add company")
    p.set_defaults(handler=lambda _: handle_add_company())

REGISTRY.register_group("add", build_add_company)
