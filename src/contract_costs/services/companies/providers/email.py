from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from contract_costs.unit_of_work import UnitOfWork


class EmailCandidateProvider(CompanyCandidateProvider):

    # def __init__(self, company_repository: CompanyRepository) -> None:
    #     self._repo = company_repository

    def find_candidates(
            self,
            *,
            uow: UnitOfWork,
            organization_id: UUID,
            input_: CompanyInput,
    ) -> list[Company]:
        if not input_.email:
            return []

        return uow.companies.find_by_email(
            organization_id=organization_id,
            email=input_.email)
