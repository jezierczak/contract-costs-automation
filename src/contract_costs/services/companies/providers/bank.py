from typing import Iterable

from contract_costs.model.company import Company
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_bank_account
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.invoices.dto.parse import CompanyInput




class BankAccountCandidateProvider(CompanyCandidateProvider):

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._repo = company_repository

    def find_candidates(self, input_: CompanyInput) -> list[Company]:
        if not input_.bank_account:
            return []

        normalized = normalize_bank_account(input_.bank_account)
        if normalized:
            return self._repo.find_by_bank_account(normalized)
        return []
