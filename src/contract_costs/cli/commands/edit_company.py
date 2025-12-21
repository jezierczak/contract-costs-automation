from contract_costs.cli.prompts.interactive import interactive_prompt
from contract_costs.cli.schemas.company import COMPANY_FIELDS
from contract_costs.cli.context import get_services
from contract_costs.cli.adapters.company_adapter import update_company_from_cli
from copy import deepcopy
from contract_costs.model.company import Company


def handle_edit_company() -> None:
    services = get_services()

    tax_number = input("Type company tax number (NIP) to edit:\n-> ").strip()
    company = services.company_repository.get_by_tax_number(tax_number)

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
        company=company,
        data=data,
        change_role_service=services.change_company_role,
    )

    print("\nCompany updated successfully.")


def _prefill_company_fields(company: Company) -> list[dict]:
    fields = deepcopy(COMPANY_FIELDS)

    defaults = {
        "name": company.name,
        "tax_number": company.tax_number,
        "description": company.description,
        "address_street": company.address.street,
        "address_city": company.address.city,
        "address_zip_code": company.address.zip_code,
        "address_country": company.address.country,
        "bank_account_number": company.bank_account.number if company.bank_account else None,
        "bank_account_country_code": company.bank_account.country_code if company.bank_account else None,
        "role": company.role,
        "is_active": company.is_active,
    }

    for field in fields:
        field["default"] = defaults.get(field["name"])

    return fields
