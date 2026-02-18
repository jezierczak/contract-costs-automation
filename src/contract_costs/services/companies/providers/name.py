from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from contract_costs.services.companies.normalize.name import normalize_company_name
from contract_costs.unit_of_work import UnitOfWork


class NameCandidateProvider(CompanyCandidateProvider):
    """
    Fuzzy provider po nazwie firmy.

    ⚠️ Najsłabszy provider jakościowo:
    - używany tylko jako fallback
    - może zwracać wiele kandydatów
    """
    #
    # def __init__(self, company_repository: CompanyRepository) -> None:
    #     self._repo = company_repository

    def find_candidates(
        self,
        *,
        uow: UnitOfWork,
        organization_id: UUID,
        input_: CompanyInput,
    ) -> list[Company]:

        if not input_.name or len(input_.name.strip()) < 2:
            return []

        normalized_input = normalize_company_name(input_.name)
        if not normalized_input:
            return []

        candidates: list[Company] = []

        # ⚠️ TYLKO w obrębie organizacji
        for company in uow.companies.list_all(organization_id):
            if not company.name:
                continue

            normalized_company = normalize_company_name(company.name)
            if not normalized_company:
                continue

            # 🎯 twardy match rdzenia
            if normalized_input == normalized_company:
                candidates.append(company)
                continue

            # 🔹 miękki match (fallback)
            if (
                normalized_input in normalized_company
                or normalized_company in normalized_input
            ):
                candidates.append(company)

        return candidates
