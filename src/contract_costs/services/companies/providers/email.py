from typing import Iterable

from contract_costs.model.company import Company
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.invoices.dto.parse import CompanyInput


class EmailCandidateProvider(CompanyCandidateProvider):

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._repo = company_repository

    def find_candidates(self, input_: CompanyInput) -> list[Company]:
        if not input_.email:
            return []

        return self._repo.find_by_email(input_.email.lower())
