from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.commands.add.add_contract import handle_add_contract

def build_add_contract(subparsers):
    p = subparsers.add_parser("contract", help="Add contract")
    p.set_defaults(handler=lambda _: handle_add_contract())

REGISTRY.register_group("add", build_add_contract)
