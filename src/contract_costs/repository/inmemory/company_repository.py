from typing import Any, Generator
from uuid import UUID

from contract_costs.model.company import Company, CompanyType
from contract_costs.repository.company_repository import CompanyRepository


class InMemoryCompanyRepository(CompanyRepository):

    def __init__(self) -> None:
        self._companies: dict[UUID, Company] = {}

    def add(self, company: Company) -> None:
        self._companies[company.id] = company

    def get(self, company_id: UUID) -> Company | None:
        return self._companies.get(company_id)

    def get_by_tax_number(self, tax_number: str) -> Company | None:
        for company in self._companies.values():
            if company.tax_number == tax_number:
                return company
        return None

    def list(self) -> list[Company]:
        return list(self._companies.values())

    def update(self, company: Company) -> None:
        self._companies[company.id] = company

    def exists(self, company_id: UUID) -> bool:
        return company_id in self._companies

    def exists_owner(self) -> bool:
        return any(
            c.role == CompanyType.OWN and c.is_active
            for c in self._companies.values()
        )
