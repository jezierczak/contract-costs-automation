from contract_costs.cli.adapters.cost_type_adapter import update_cost_type_from_cli, deactivate_cost_type_from_cli
from contract_costs.cli.registry import REGISTRY
from types import SimpleNamespace
from contract_costs.cli.context import get_services
from contract_costs.cli.prompts.interactive import interactive_prompt


def build_edit_cost_type(subparsers):
    p = subparsers.add_parser("cost-type", help="Edit cost type")
    p.add_argument("--deactivate", action="store_true")
    p.set_defaults(handler=handle_edit_cost_type)

REGISTRY.register_group("edit", build_edit_cost_type)


def handle_edit_cost_type(args=None) -> None:
    if args is None:
        args = SimpleNamespace(deactivate=False)

    services = get_services()
    repo = services.cost_type_repository

    code = input("Type cost type code:\n-> ").strip()
    cost_type = repo.get_by_code(code)

    if cost_type is None:
        print("Cost type not found.")
        return

    if args.deactivate:
        deactivate_cost_type_from_cli(
            cost_type=cost_type,
            deactivate_cost_type_service=services.deactivate_cost_type_service,
        )
        print("Cost type deactivated.")
        return

    fields = [
        {
            "name": "name",
            "prompt": "Name",
            "type": str,
            "required": True,
            "default": cost_type.name,
        },
        {
            "name": "description",
            "prompt": "Description",
            "type": str,
            "required": False,
            "default": cost_type.description,
        },
    ]

    data = interactive_prompt(fields)

    confirm = input("\nConfirm update? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    update_cost_type_from_cli(
        cost_type=cost_type,
        data=data,
        update_cost_type_service=services.update_cost_type_service,
    )

    print("Cost type updated.")

