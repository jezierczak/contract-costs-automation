from contract_costs.model.company import Company
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.invoices.dto.parse import CompanyInput
from contract_costs.services.companies.normalize.name import normalize_company_name

class NameCandidateProvider(CompanyCandidateProvider):

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._repo = company_repository

    def find_candidates(self, input_: CompanyInput) -> list[Company]:
        if not input_.name or len(input_.name) < 3:
            return []

        normalized_input = normalize_company_name(input_.name)
        if not normalized_input:
            return []

        candidates: list[Company] = []

        for company in self._repo.list_all():
            normalized_company = normalize_company_name(company.name)
            if not normalized_company:
                continue

            # 🎯 twardy match rdzenia
            if normalized_input == normalized_company:
                candidates.append(company)
                continue

            # 🔹 luźniejszy match (opcjonalny, ale polecam)
            if (
                normalized_input in normalized_company
                or normalized_company in normalized_input
            ):
                candidates.append(company)

        return candidates
