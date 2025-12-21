from dataclasses import replace
from uuid import UUID

from contract_costs.model.company import CompanyType
from contract_costs.repository.company_repository import CompanyRepository


class ChangeCompanyRoleService:

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._companies = company_repository

    def execute(self, company_id: UUID, new_role: CompanyType) -> None:
        company = self._companies.get(company_id)
        if company is None:
            raise ValueError("Company does not exist")

        updated = replace(company, role=new_role)
        self._companies.update(updated)
