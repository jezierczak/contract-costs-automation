from uuid import UUID

from contract_costs.model.company import Company, CompanyType
from contract_costs.repository.company_repository import CompanyRepository


class InMemoryCompanyRepository(CompanyRepository):

    def __init__(self) -> None:
        self._companies: dict[UUID, Company] = {}

    # ---------- CRUD ----------

    def add(self, company: Company) -> None:
        self._companies[company.id] = company

    def update(self, company: Company) -> None:
        if company.id not in self._companies:
            raise KeyError("Company does not exist")

        self._companies[company.id] = company

    def delete(self, company_id: UUID, organization_id: UUID) -> None:
        company = self._companies.get(company_id)
        if company and company.organization_id == organization_id:
            self._companies.pop(company_id, None)

    def get(self, company_id: UUID, organization_id: UUID) -> Company | None:
        company = self._companies.get(company_id)
        if company and company.organization_id == organization_id:
            return company
        return None

    def list_all(self, organization_id: UUID) -> list[Company]:
        return [
            c for c in self._companies.values()
            if c.organization_id == organization_id
        ]

    def exists(self, company_id: UUID, organization_id: UUID) -> bool:
        company = self._companies.get(company_id)
        return bool(company and company.organization_id == organization_id)

    # ---------- identity ----------

    def get_by_tax_number(self, tax_number: str, organization_id: UUID) -> Company | None:
        for company in self._companies.values():
            if (
                company.organization_id == organization_id
                and company.tax_number == tax_number
            ):
                return company
        return None

    def get_owners(self, organization_id: UUID) -> list[Company]:
        return [
            c for c in self._companies.values()
            if (
                c.organization_id == organization_id
                and c.role == CompanyType.OWN
                and c.is_active
            )
        ]

    def exists_owner(self, organization_id: UUID) -> bool:
        return any(
            c.organization_id == organization_id
            and c.role == CompanyType.OWN
            and c.is_active
            for c in self._companies.values()
        )

    # ---------- candidate search ----------

    def find_by_bank_account(
        self,
        organization_id: UUID,
        bank_account_number: str,
    ) -> list[Company]:
        return [
            c for c in self._companies.values()
            if (
                c.organization_id == organization_id
                and c.bank_account
                and c.bank_account.account_number == bank_account_number
            )
        ]

    def find_by_email(
        self,
        organization_id: UUID,
        email: str,
    ) -> list[Company]:
        return [
            c for c in self._companies.values()
            if (
                c.organization_id == organization_id
                and c.contact
                and c.contact.email == email
            )
        ]

    def find_by_phone(
        self,
        organization_id: UUID,
        phone_number: str,
    ) -> list[Company]:
        return [
            c for c in self._companies.values()
            if (
                c.organization_id == organization_id
                and c.contact
                and c.contact.phone_number == phone_number
            )
        ]

    def find_by_name_like(
        self,
        organization_id: UUID,
        name: str,
    ) -> list[Company]:
        name_lower = name.lower()
        return [
            c for c in self._companies.values()
            if (
                c.organization_id == organization_id
                and c.name
                and name_lower in c.name.lower()
            )
        ]

    def find_by_street_tokens(
        self,
        organization_id: UUID,
        tokens: list[str],
    ) -> list[Company]:
        if not tokens:
            return []

        tokens_lower = [t.lower() for t in tokens]
        result: list[Company] = []

        for company in self._companies.values():
            if company.organization_id != organization_id:
                continue
            if not company.address or not company.address.street:
                continue

            street = company.address.street.lower()
            if all(token in street for token in tokens_lower):
                result.append(company)

        return result
