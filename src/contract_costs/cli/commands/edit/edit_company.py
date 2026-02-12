import logging
from types import SimpleNamespace
from uuid import UUID

from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.schemas.company import COMPANY_FIELDS
from contract_costs.cli.context import get_services
from contract_costs.cli.adapters.company_adapter import update_company_from_cli
from copy import deepcopy

from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.model.company import Company
from contract_costs.services.common.resolve_utils import normalize_required_tax_number
from contract_costs.services.companies.dto.activate_company_command import ActivateCompanyCommand
from contract_costs.services.companies.dto.deactivate_company_command import DeactivateCompanyCommand

logger = logging.getLogger(__name__)


def handle_edit_company(args=None) -> None:
    # =====================
    # NORMALIZE ARGS
    # =====================
    if args is None:
        args = SimpleNamespace(
            activate=False,
            deactivate=False,
            id=None,
            nip=None,
        )
    if args.activate or args.deactivate:
        _handle_company_status_change(args)
        return

    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    if args.id:
        company = services.company_repository.get(
            UUID(args.id),
            organization_id
        )
    elif args.nip:
        tax_number = normalize_required_tax_number(args.nip)
        company = services.company_repository.get_by_tax_number(
            tax_number=tax_number,
            organization_id=organization_id,
        )
    else:
        tax_number = normalize_required_tax_number(
            input("Type company tax number (NIP) to edit:\n-> ").strip()
        )

        company = services.company_repository.get_by_tax_number(
            tax_number,
            organization_id
        )

    if company is None:
        print("Company not found.")
        return

    print("\nEditing company. Leave field empty to keep current value.\n")

    # Prefill defaults from existing company
    fields = _prefill_company_fields(company)

    data = interactive_prompt(fields)

    print("\nUpdated company data:")
    for k, v in data.items():
        print(f"  {k}: {v}")

    confirm = input("\nConfirm update? (y/n): ").strip().lower()
    if confirm != "y":
        print("Operation cancelled.")
        return

    update_company_from_cli(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        company=company,
        data=data,
        action_bus=services.action_bus,
        update_company_service=services.update_company_service,
    )

    logger.info("\nCompany updated successfully.")


def _prefill_company_fields(company: Company) -> list[dict]:
    fields = deepcopy(COMPANY_FIELDS)

    defaults = {
        "name": company.name,
        "tax_number": company.tax_number,
        "description": company.description,
        "address_street": company.address.street if company.address else None,
        "address_city": company.address.city if company.address else None,
        "address_zip_code": company.address.zip_code if company.address else None,
        "address_country": company.address.country if company.address else None,
        "phone_number": company.contact.phone_number if company.contact else None,
        "email": company.contact.email if company.contact else None,
        "bank_account_number": company.bank_account.account_number if company.bank_account else None,
        "bank_account_country_code": company.bank_account.country_code if company.bank_account else None,
        "role": company.role,
        "is_active": company.is_active,
    }

    for field in fields:
        name = field["name"]
        assert isinstance(name, str)
        field["default"] = defaults.get(name)

    return fields



def _handle_company_status_change(args) -> None:
    services = get_services()

    organization_id = require_organization_id(services.context)
    actor_user_id = require_user_id(services.context)

    if args.activate and args.deactivate:
        print("Cannot activate and deactivate at the same time")
        return

    # resolve company
    if args.id:
        company_id = UUID(args.id)
    else:
        tax_number = normalize_required_tax_number(args.nip)
        company = services.company_repository.get_by_tax_number(tax_number=tax_number,organization_id=organization_id)
        if company is None:
            print("Company not found")
            return
        company_id = company.id


    if args.activate:
        activate_cmd = ActivateCompanyCommand(
            organization_id=organization_id,
            company_id=company_id,
            actor_user_id=actor_user_id,
        )

        services.activate_company_service.execute(activate_cmd)
        print("Company activated")
    else:
        deactivate_cmd = DeactivateCompanyCommand(
            organization_id=organization_id,
            company_id=company_id,
            actor_user_id=actor_user_id,
        )

        services.deactivate_company_service.execute(deactivate_cmd)
        print("Company deactivated")