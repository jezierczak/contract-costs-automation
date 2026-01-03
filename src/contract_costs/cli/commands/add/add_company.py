import logging

from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.schemas.company import COMPANY_FIELDS
from contract_costs.cli.adapters.company_adapter import create_company_from_cli
from contract_costs.cli.context import get_services

logger = logging.getLogger(__name__)

def handle_add_company() -> None:
    print("\nAdding companies service:\n")

    data = interactive_prompt(COMPANY_FIELDS)

    print("\nCompany data to add:")
    for key, value in data.items():
        print(f"  {key}: {value}")

    confirm = input("\nConfirm add companies? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    services = get_services()

    create_company_from_cli(
        data=data,
        create_company_service=services.create_company,
    )

    logger.info("\nCompany added successfully.")
