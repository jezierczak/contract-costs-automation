import logging

from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.schemas.organization import ORGANIZATION_FIELDS
from contract_costs.cli.adapters.organization_adapter import create_organization_from_cli
from contract_costs.cli.context import get_services

logger = logging.getLogger(__name__)

def build_add_organization(subparsers):
    p = subparsers.add_parser("organization", help="Add organization")
    p.set_defaults(handler=handle_add_organization)


REGISTRY.register_group("add", build_add_organization)

def handle_add_organization(args=None):
    if args is not None and getattr(args, "non_interactive", False):
        return

    _run_add_organization_interactive()


def _run_add_organization_interactive() -> None:
    print("\nAdding organization:\n")

    data = interactive_prompt(ORGANIZATION_FIELDS)

    print("\nOrganization data to add:")
    for key, value in data.items():
        print(f"  {key}: {value}")

    confirm = input("\nConfirm add organization? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return



    create_organization_from_cli(
        data=data
    )


    logger.info("Organization added successfully.")
