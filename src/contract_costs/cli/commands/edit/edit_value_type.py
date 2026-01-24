from contract_costs.cli.adapters.value_type_adapter import update_value_type_from_cli, deactivate_value_type_from_cli
from contract_costs.cli.registry import REGISTRY
from types import SimpleNamespace
from contract_costs.cli.context import get_services
from contract_costs.cli.prompts.interactive import interactive_prompt


def build_edit_value_type(subparsers):
    p = subparsers.add_parser("value-type", help="Edit value type")
    p.add_argument("--deactivate", action="store_true")
    p.set_defaults(handler=handle_edit_value_type)

REGISTRY.register_group("edit", build_edit_value_type)


def handle_edit_value_type(args=None) -> None:
    if args is None:
        args = SimpleNamespace(deactivate=False)

    services = get_services()
    repo = services.value_type_repository

    code = input("Type value type code:\n-> ").strip()
    value_type = repo.get_by_code(code)

    if value_type is None:
        print("Value type not found.")
        return

    if args.deactivate:
        deactivate_value_type_from_cli(
            value_type=value_type,
            deactivate_value_type_service=services.deactivate_value_type_service,
        )
        print("Value type deactivated.")
        return

    fields = [
        {
            "name": "name",
            "prompt": "Name",
            "type": str,
            "required": True,
            "default": value_type.name,
        },
        {
            "name": "description",
            "prompt": "Description",
            "type": str,
            "required": False,
            "default": value_type.description,
        },
    ]

    data = interactive_prompt(fields)

    confirm = input("\nConfirm update? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    update_value_type_from_cli(
        value_type=value_type,
        data=data,
        update_value_type_service=services.update_value_type_service,
    )

    print("Value type updated.")

