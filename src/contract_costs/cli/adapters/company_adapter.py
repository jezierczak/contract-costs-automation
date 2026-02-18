from uuid import UUID

from contract_costs.action_bus.action_bus import ActionBus
from contract_costs.model.company import Address, Company, Contact, CompanyType
from contract_costs.model.company import BankAccount
from contract_costs.services.companies.dto.create_company_command import (
    CreateCounterpartyCompanyCommand,
    CreateOwnerCompanyCommand,
)
from contract_costs.services.companies.dto.update_company_command import (
    UpdateCounterpartyCompanyCommand,
    UpdateOwnerCompanyCommand,
)
from contract_costs.services.companies.update_company_service import UpdateCompanyService
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.unit_of_work import UnitOfWork


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

    create_cmd_type = (
        CreateOwnerCompanyCommand
        if data["role"] == CompanyType.OWN
        else CreateCounterpartyCompanyCommand
    )

    cmd = create_cmd_type(
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
    action_bus.execute(action=cmd, handler=create_company_service)
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

    update_cmd_type = (
        UpdateOwnerCompanyCommand
        if data["role"] == CompanyType.OWN
        else UpdateCounterpartyCompanyCommand
    )

    cmd = update_cmd_type(
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

    # TU później:
    # - change address
    # - change bank account
    # - activate/deactivate
