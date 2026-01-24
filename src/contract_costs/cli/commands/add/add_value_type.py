import logging

from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.schemas.value_type import VALUE_TYPE_FIELDS
from contract_costs.cli.adapters.value_type_adapter import create_value_type_from_cli
from contract_costs.cli.context import get_services

logger = logging.getLogger(__name__)


def handle_add_value_type(args=None) -> None:
    print("\nAdding value type:\n")

    data = interactive_prompt(VALUE_TYPE_FIELDS)

    print("\nValue type data to add:")
    for k, v in data.items():
        print(f"  {k}: {v}")

    confirm = input("\nConfirm add value type? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    services = get_services()

    create_value_type_from_cli(
        data=data,
        create_value_type_service=services.create_value_type,
    )

    logger.info("\nCost type added successfully.")
