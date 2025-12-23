from dataclasses import replace
from uuid import UUID

from contract_costs.model.company import CompanyType, CompanyTag, BankAccount, Address
from contract_costs.repository.company_repository import CompanyRepository


class UpdateCompanyService:

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._companies = company_repository

    def execute(self, company_id: UUID,
                *,
        name: str,
        address: Address,
        role: CompanyType,
        description: str | None = None,
        bank_account: BankAccount | None = None,
        tags: set[CompanyTag] | None = None,) -> None:
        company = self._companies.get(company_id)
        if company is None:
            raise ValueError("Company does not exist")

        updated = replace(company,
                          name=name,
                          address=address,
                          description=description,
                          bank_account=bank_account,
                          tags=tags,
                          role=role)
        self._companies.update(updated)
