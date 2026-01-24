from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.services.value_types.apply.commands.change_value_type_code_command import ChangeValueTypeCodeCommand


def build_change_value_type_code(subparsers):
    p = subparsers.add_parser(
        "value-type-code",
        help="Change value type code (dangerous)",
    )
    p.set_defaults(handler=handle_change_value_type_code)

REGISTRY.register_group("edit", build_change_value_type_code)


def handle_change_value_type_code(args=None) -> None:
    services = get_services()
    repo = services.value_type_repository

    code = input("Current cost type code:\n-> ").strip()
    value_type = repo.get_by_code(code)

    if value_type is None:
        print("Value type not found.")
        return

    print(
        "\n⚠ WARNING ⚠\n"
        "Changing value type code may affect reports and contracts.\n"
    )

    new_code = input("New code:\n-> ").strip()

    confirm = input(
        f"\nConfirm change code '{value_type.code}' → '{new_code}' ? (y/n): "
    ).lower()

    if confirm != "y":
        print("Operation cancelled.")
        return

    cmd = ChangeValueTypeCodeCommand(
        value_type_id=value_type.id,
        new_code=new_code,
    )

    services.change_value_type_code_service.execute(cmd)

    print("Cost type code changed.")
