from uuid import uuid4

from contract_costs.model.company import Company, CompanyType, Address, BankAccount, CompanyTag
from contract_costs.repository.company_repository import CompanyRepository


class CreateCompanyService:

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._companies = company_repository

    def execute(
        self,
        *,
        name: str,
        tax_number: str,
        address: Address,
        role: CompanyType,
        description: str | None = None,
        bank_account: BankAccount | None = None,
        tags: set[CompanyTag] | None = None,
    ) -> Company:
        if self._companies.get_by_tax_number(tax_number):
            raise ValueError("Company with this tax number already exists")

        company = Company(
            id=uuid4(),
            name=name,
            description=description,
            tax_number=tax_number,
            address=address,
            bank_account=bank_account,
            role=role,
            tags=tags or set(),
            is_active=True,
        )

        self._companies.add(company)
        return company
