

import re
from contract_costs.model.company import Company
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_phone
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.invoices.dto.parse import CompanyInput


class PhoneCandidateProvider(CompanyCandidateProvider):

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._repo = company_repository

    def find_candidates(self, input_: CompanyInput) -> list[Company]:
        if not input_.phone_number:
            return []

        normalized = normalize_phone(input_.phone_number)
        if normalized:
            return self._repo.find_by_phone(normalized)
        return []



