from contract_costs.model.company import Address, Company
from contract_costs.model.company import BankAccount
from contract_costs.services.companies.update_company_service import UpdateCompanyService
from contract_costs.services.companies.create_company_service import CreateCompanyService


def create_company_from_cli(
    *,
    data: dict,
    create_company_service: CreateCompanyService,
) -> None:
    """
    Adapter: CLI data -> CreateCompanyService
    """

    # --- Address ---
    address = Address(
        street=data["address_street"],
        city=data["address_city"],
        zip_code=data["address_zip_code"],
        country=data["address_country"],
    )

    # --- Bank account (optional) ---
    bank_account = None
    if data.get("bank_account_number"):
        bank_account = BankAccount(
            number=data["bank_account_number"],
            country_code=data.get("bank_account_country_code"),
        )

    # --- Execute service ---
    create_company_service.execute(
        name=data["name"],
        tax_number=data["tax_number"],
        description=data.get("description"),
        address=address,
        bank_account=bank_account,
        role=data["role"],
    )

def update_company_from_cli(
    *,
    company: Company,
    data: dict,
    update_company_service: UpdateCompanyService,
) -> None:
    """
    Adapter CLI -> change services
    """
    # --- Address ---
    address = Address(
        street=data["address_street"],
        city=data["address_city"],
        zip_code=data["address_zip_code"],
        country=data["address_country"],
    )

    # --- Bank account (optional) ---
    bank_account = None
    if data.get("bank_account_number"):
        bank_account = BankAccount(
            number=data["bank_account_number"],
            country_code=data.get("bank_account_country_code"),
        )

    # ---- role change ----
    if data["role"] != company.role:
        update_company_service.execute(
            company_id=company.id,
            name=data["name"],
            description=data.get("description"),
            address=address,
            bank_account=bank_account,
            role=data["role"],
        )

    # TU później:
    # - change address
    # - change bank account
    # - activate/deactivate