from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.commands.edit.edit_company import handle_edit_company

def build_edit_company(subparsers):
    p = subparsers.add_parser("company", help="Edit company")
    p.set_defaults(handler=lambda _: handle_edit_company())

REGISTRY.register_group("edit", build_edit_company)
