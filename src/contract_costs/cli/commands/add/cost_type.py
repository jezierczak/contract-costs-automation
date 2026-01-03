from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.commands.add.add_cost_type import handle_add_cost_type

def build_add_cost_type(subparsers):
    p = subparsers.add_parser("cost-type", help="Add cost type")
    p.set_defaults(handler=lambda _: handle_add_cost_type())

REGISTRY.register_group("add", build_add_cost_type)
