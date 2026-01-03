import logging
from datetime import date
from pathlib import Path
import contract_costs.config as cfg

from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.schemas.contract import CONTRACT_FIELDS
from contract_costs.cli.context import get_services
from contract_costs.model.contract import ContractStarter

logger = logging.getLogger(__name__)


def handle_add_contract() -> None:
    services = get_services()

    print("\nAdding contract:\n")

    # --- select owner ---
    owner_tax = input("Owner company NIP:\n-> ").strip()
    owner = services.company_repository.get_by_tax_number(owner_tax)

    if owner is None:
        print("Owner company not found.")
        return

    # --- select client ---
    client_tax = input("Client company NIP:\n-> ").strip()
    client = services.company_repository.get_by_tax_number(client_tax)

    if client is None:
        print("Client company not found.")
        print("Continuing without client.")

    data = interactive_prompt(CONTRACT_FIELDS)

    print("\nContract data to add:")
    for k, v in data.items():
        print(f"  {k}: {v}")

    confirm = input("\nConfirm add contract? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    starter = ContractStarter(
        name=data["name"],
        code=data["code"],
        description=data.get("description"),
        contract_owner=owner,
        client=client,
        start_date=_parse_date(data.get("start_date")),
        end_date=_parse_date(data.get("end_date")),
        budget=data.get("budget"),
        path=_contract_path(cfg.OWNERS_DIR, owner.name),
        status=data["status"],
    )

    service = services.create_contract
    service.init(starter)
    service.execute()

    logger.info("\nContract created successfully.")

def _parse_date(value: str | None):
    if not value:
        return None
    return date.fromisoformat(value)


def _contract_path(owner, contract_name: str) -> Path:
    safe_name = contract_name.replace(" ", "_").lower()
    return Path(owner.name) / safe_name

