from uuid import UUID

from contract_costs.action_bus.action_bus import ActionBus
from contract_costs.model.company import Address, Company, Contact
from contract_costs.model.company import BankAccount
from contract_costs.services.companies.dto.create_company_command import CreateCompanyCommand
from contract_costs.services.companies.dto.update_company_command import UpdateCompanyCommand
from contract_costs.services.companies.update_company_service import UpdateCompanyService
from contract_costs.services.companies.create_company_service import CreateCompanyService


def create_company_from_cli(
    *,
    data: dict,
    organization_id: UUID,
    actor_user_id: UUID,
    action_bus: ActionBus,
    create_company_service: CreateCompanyService,
) -> None:
    address = Address(
        street=data["address_street"],
        city=data["address_city"],
        zip_code=data["address_zip_code"],
        country=data["address_country"],
    )

    contact = Contact(
        phone_number=data["phone_number"],
        email=data["email"],
    )

    bank_account = (
        BankAccount(
            account_number=data["bank_account_number"],
            country_code=data.get("bank_account_country_code"),
        )
        if data.get("bank_account_number")
        else None
    )

    cmd = CreateCompanyCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,

        name=data["name"],
        tax_number=data["tax_number"],
        role=data["role"],

        description=data.get("description"),
        address=address,
        contact=contact,
        bank_account=bank_account,
        tags=None,
    )
    action_bus.execute(action=cmd,handler=create_company_service)
    # create_company_service.execute(cmd)

def update_company_from_cli(
    *,
    company: Company,
    data: dict,
    organization_id: UUID,
    actor_user_id: UUID,
    action_bus: ActionBus,
    update_company_service: UpdateCompanyService,
) -> None:
    address = Address(
        street=data["address_street"],
        city=data["address_city"],
        zip_code=data["address_zip_code"],
        country=data["address_country"],
    )

    contact = Contact(
        phone_number=data["phone_number"],
        email=data["email"],
    )

    bank_account = (
        BankAccount(
            account_number=data["bank_account_number"],
            country_code=data.get("bank_account_country_code"),
        )
        if data.get("bank_account_number")
        else None
    )

    cmd = UpdateCompanyCommand(
        organization_id=organization_id,
        company_id=company.id,
        actor_user_id=actor_user_id,

        name=data["name"],
        role=data["role"],
        address=address,
        contact=contact,
        description=data.get("description"),
        tax_number=data.get("tax_number"),
        bank_account=bank_account,
        tags=None,
    )
    action_bus.execute(
        action=cmd,
        handler=update_company_service)
    update_company_service.execute(cmd)

    # TU później:
    # - change address
    # - change bank account
    # - activate/deactivate