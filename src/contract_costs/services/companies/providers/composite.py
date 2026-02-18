import logging
from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class CompositeCompanyCandidateProvider(CompanyCandidateProvider):

    def __init__(self, providers: list[CompanyCandidateProvider]) -> None:
        self._providers = providers

    def find_candidates(
        self,
        *,
        uow: UnitOfWork,
        organization_id: UUID,
        input_: CompanyInput,
    ) -> list[Company]:
        result: dict[UUID, Company] = {}

        for provider in self._providers:
            for company in provider.find_candidates(
                uow=uow,
                organization_id=organization_id,
                input_=input_,
            ):
                result[company.id] = company  # deduplikacja po ID

        return list(result.values())
