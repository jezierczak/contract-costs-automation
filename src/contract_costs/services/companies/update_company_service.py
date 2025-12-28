from dataclasses import replace
from uuid import UUID

from contract_costs.model.company import CompanyType, BankAccount, Address, Contact
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_required_tax_number


class UpdateCompanyService:

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._companies = company_repository

    def execute(
            self,
            company_id: UUID,
            *,
            name: str,
            address: Address,
            contact: Contact | None = None,
            role: CompanyType,
            tax_number: str | None = None,
            description: str | None = None,
            bank_account: BankAccount | None = None,
            tags: set[str] | None = None,
    ) -> None:
        company = self._companies.get(company_id)
        if company is None:
            raise ValueError("Company does not exist")
        normalized: str
        if tax_number is None:
            normalized = company.tax_number
        else:
            normalized = normalize_required_tax_number(tax_number)

            existing = self._companies.get_by_tax_number(normalized)
            if existing and existing.id != company_id:
                raise ValueError("Company with this tax number already exists")

        updated = replace(
            company,
            name=name,
            tax_number=normalized,
            address=address,
            contact=contact,
            description=description,
            bank_account=bank_account,
            tags=tags,
            role=role,
        )

        self._companies.update(updated)
