from uuid import UUID

from contract_costs.repository.company_repository import CompanyRepository


class DeactivateCompanyService:
    def __init__(self, company_repository: CompanyRepository) -> None:
        self._companies = company_repository

    def execute(self, company_id: UUID) -> None:
        company = self._companies.get(company_id)
        if company is None:
            raise ValueError("Company does not exist")

        if not company.is_active:
            # idempotent
            return

        updated = company.__class__(
            **{
                **company.__dict__,
                "is_active": False,
            }
        )

        self._companies.update(updated)
