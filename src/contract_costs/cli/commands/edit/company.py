from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.commands.edit.edit_company import handle_edit_company

def build_edit_company(subparsers):
    p = subparsers.add_parser("company", help="Edit company")

    p.add_argument("--activate", action="store_true", help="Activate company")
    p.add_argument("--deactivate", action="store_true", help="Deactivate company")

    p.add_argument("--id", help="Company UUID")
    p.add_argument("--nip", help="Company tax number")

    p.set_defaults(handler=handle_edit_company)

REGISTRY.register_group("edit", build_edit_company)
