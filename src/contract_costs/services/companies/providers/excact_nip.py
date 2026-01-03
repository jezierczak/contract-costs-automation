from typing import Iterable
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.invoices.dto.parse import CompanyInput
from contract_costs.model.company import Company
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_tax_number


class ExactNipCandidateProvider(CompanyCandidateProvider):
    """
    Najprostszy możliwy provider:
    - szuka tylko po dokładnym NIP
    """

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._repo = company_repository

    def find_candidates(self, input_: CompanyInput) -> list[Company]:
        if not input_.tax_number:
            return []

        tax = normalize_tax_number(input_.tax_number)
        if tax:
            company = self._repo.get_by_tax_number(tax)
            if company:
                return [company]
        return []
