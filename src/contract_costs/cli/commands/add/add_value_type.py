import logging

from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.schemas.value_type import VALUE_TYPE_FIELDS
from contract_costs.cli.adapters.value_type_adapter import create_value_type_from_cli
from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError

logger = logging.getLogger(__name__)


def handle_add_value_type(args=None) -> None:


    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    print("\nAdding value type:\n")

    data = interactive_prompt(VALUE_TYPE_FIELDS)

    print("\nValue type data to add:")
    for k, v in data.items():
        print(f"  {k}: {v}")

    confirm = input("\nConfirm add value type? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    create_value_type_from_cli(
        data=data,
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        create_value_type_service=services.create_value_type,
    )

    logger.info("\nCost type added successfully.")
