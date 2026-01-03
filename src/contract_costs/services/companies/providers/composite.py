import logging
from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.invoices.dto.parse import CompanyInput

logger = logging.getLogger(__name__)


class CompositeCompanyCandidateProvider(CompanyCandidateProvider):

    def __init__(self, providers: list[CompanyCandidateProvider]) -> None:
        self._providers = providers

    def find_candidates(self, input_: CompanyInput) -> list[Company]:
        result: dict[UUID, Company] = {}

        for provider in self._providers:
            for company in provider.find_candidates(input_):
                result[company.id] = company  # nadpisanie = deduplikacja
        return list(result.values())
