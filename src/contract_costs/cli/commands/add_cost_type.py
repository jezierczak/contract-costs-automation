from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.schemas.cost_type import COST_TYPE_FIELDS
from contract_costs.cli.adapters.cost_type_adapter import create_cost_type_from_cli
from contract_costs.cli.context import get_services


def handle_add_cost_type() -> None:
    print("\nAdding cost type:\n")

    data = interactive_prompt(COST_TYPE_FIELDS)

    print("\nCost type data to add:")
    for k, v in data.items():
        print(f"  {k}: {v}")

    confirm = input("\nConfirm add cost type? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    services = get_services()

    create_cost_type_from_cli(
        data=data,
        create_cost_type_service=services.create_cost_type,
    )

    print("\nCost type added successfully.")
