from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.services.cost_types.apply.commands.change_cost_type_code_command import ChangeCostTypeCodeCommand


def build_change_cost_type_code(subparsers):
    p = subparsers.add_parser(
        "cost-type-code",
        help="Change cost type code (dangerous)",
    )
    p.set_defaults(handler=handle_change_cost_type_code)

REGISTRY.register_group("edit", build_change_cost_type_code)


def handle_change_cost_type_code(args=None) -> None:
    services = get_services()
    repo = services.cost_type_repository

    code = input("Current cost type code:\n-> ").strip()
    cost_type = repo.get_by_code(code)

    if cost_type is None:
        print("Cost type not found.")
        return

    print(
        "\n⚠ WARNING ⚠\n"
        "Changing cost type code may affect reports and contracts.\n"
    )

    new_code = input("New code:\n-> ").strip()

    confirm = input(
        f"\nConfirm change code '{cost_type.code}' → '{new_code}' ? (y/n): "
    ).lower()

    if confirm != "y":
        print("Operation cancelled.")
        return

    cmd = ChangeCostTypeCodeCommand(
        cost_type_id=cost_type.id,
        new_code=new_code,
    )

    services.change_cost_type_code_service.execute(cmd)

    print("Cost type code changed.")
