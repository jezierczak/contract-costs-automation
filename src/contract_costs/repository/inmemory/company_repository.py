from uuid import UUID
from typing import Iterable

from contract_costs.model.company import Company, CompanyType
from contract_costs.repository.company_repository import CompanyRepository


class InMemoryCompanyRepository(CompanyRepository):

    def __init__(self) -> None:
        self._companies: dict[UUID, Company] = {}

    # ---------- CRUD ----------

    def add(self, company: Company) -> None:
        self._companies[company.id] = company

    def update(self, company: Company) -> None:
        self._companies[company.id] = company

    def delete(self, company_id: UUID) -> None:
        self._companies.pop(company_id, None)

    def get(self, company_id: UUID) -> Company | None:
        return self._companies.get(company_id)

    def list_all(self) -> list[Company]:
        return list(self._companies.values())

    def exists(self, company_id: UUID) -> bool:
        return company_id in self._companies

    # ---------- identity ----------

    def get_by_tax_number(self, tax_number: str) -> Company | None:
        for company in self._companies.values():
            if company.tax_number == tax_number:
                return company
        return None

    def get_owners(self) -> list[Company]:
        return [
            c for c in self._companies.values()
            if c.role == CompanyType.OWN and c.is_active
        ]

    def exists_owner(self) -> bool:
        return any(
            c.role == CompanyType.OWN and c.is_active
            for c in self._companies.values()
        )

    # ---------- candidate search ----------

    def find_by_bank_account(self, bank_account: str) -> list[Company]:
        return [
            c for c in self._companies.values()
            if c.bank_account and c.bank_account == bank_account
        ]

    def find_by_email(self, email: str) -> list[Company]:
        return [
            c for c in self._companies.values()
            if c.contact and c.contact.email == email
        ]

    def find_by_phone(self, phone_number: str) -> list[Company]:
        return [
            c for c in self._companies.values()
            if c.contact and c.contact.phone_number == phone_number
        ]

    def find_by_name_like(self, name: str) -> list[Company]:
        name_lower = name.lower()
        return [
            c for c in self._companies.values()
            if c.name and name_lower in c.name.lower()
        ]


    def find_by_street_tokens(self, tokens: list[str]) -> list[Company]:
        if not tokens:
            return []

        tokens_lower = [t.lower() for t in tokens]

        result: list[Company] = []

        for company in self._companies.values():
            if not company.address or not company.address.street:
                continue

            street = company.address.street.lower()

            # 🔹 SQL-like: wszystkie tokeny muszą wystąpić
            if all(token in street for token in tokens_lower):
                result.append(company)

        return result
