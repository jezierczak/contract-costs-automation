from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.commands.add.add_value_type import handle_add_value_type

def build_add_value_type(subparsers):
    p = subparsers.add_parser("value-type", help="Add value type")
    p.set_defaults(handler=handle_add_value_type)

REGISTRY.register_group("add", build_add_value_type)
