import logging
from datetime import date

from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.schemas.contract import CONTRACT_FIELDS
from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_user_id, require_organization_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.model.contract import ContractType

from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand

logger = logging.getLogger(__name__)


def handle_add_contract(args=None) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    print("\nAdding contract:\n")

    # --- select owner ---
    owner_tax = input("Owner company NIP:\n-> ").strip()
    owner = services.company_repository.get_by_tax_number(owner_tax,organization_id)

    if owner is None:
        print("Owner company not found.")
        return

    # --- select client ---
    client_tax = input("Client company NIP:\n-> ").strip()
    client = services.company_repository.get_by_tax_number(client_tax,organization_id)

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

    command = CreateContractCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        name=data["name"],
        code=data["code"],
        description=data.get("description"),
        owner=owner,
        client=client,
        start_date=_parse_date(data.get("start_date")),
        end_date=_parse_date(data.get("end_date")),
        budget=data.get("budget"),
        path=None,
        status=data["status"],
        contract_type=ContractType.PROJECT
    )

    # service = services.create_contract
    # service.init(command)
    # service.execute()

    services.action_bus.execute(
        action=command,
        handler=services.create_contract
    )

    logger.info("\nContract created successfully.")

def _parse_date(value: str | None):
    if not value:
        return None
    return date.fromisoformat(value)


