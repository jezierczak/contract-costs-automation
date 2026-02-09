from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_phone
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput


class PhoneCandidateProvider(CompanyCandidateProvider):
    """
    Provider oparty o numer telefonu.

    ✔️ dość mocny sygnał
    ⚠️ nadal nie globalnie unikalny
    """

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._repo = company_repository

    def find_candidates(
        self,
        *,
        organization_id: UUID,
        input_: CompanyInput,
    ) -> list[Company]:

        if not input_.phone_number:
            return []

        normalized = normalize_phone(input_.phone_number)
        if not normalized:
            return []

        return self._repo.find_by_phone(
            organization_id=organization_id,
            phone_number=normalized,
        )
