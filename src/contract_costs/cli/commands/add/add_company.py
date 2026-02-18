import logging

from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.schemas.company import COMPANY_FIELDS
from contract_costs.cli.adapters.company_adapter import create_company_from_cli
from contract_costs.cli.context import get_services
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError

logger = logging.getLogger(__name__)


def handle_add_company(args=None):
    if args is not None and getattr(args, "non_interactive", False):
        return
    _run_add_company_interactive()


def _run_add_company_interactive() -> None:
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
    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return


    create_company_from_cli(
        data=data,
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action_bus=services.action_bus,
        create_company_service=services.create_company,
    )

    logger.info("\nCompany added successfully.")
