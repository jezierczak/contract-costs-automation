import re
from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import is_placeholder_identifier, normalize_tax_number
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from contract_costs.unit_of_work import UnitOfWork


class ExactNipCandidateProvider(CompanyCandidateProvider):
    """
    Najprostszy możliwy provider:
    - szuka tylko po dokładnym NIP
    - NIE tworzy
    - NIE ocenia
    """

    # def __init__(self, company_repository: CompanyRepository) -> None:
    #     self._repo = company_repository

    def find_candidates(
        self,
        *,
        uow: UnitOfWork,
        organization_id: UUID,
        input_: CompanyInput,
    ) -> list[Company]:

        if not input_.tax_number:
            return []

        # --- normalny NIP ---
        normalized = normalize_tax_number(input_.tax_number)
        if normalized:
            company = uow.companies.get_by_tax_number(
                tax_number=normalized,
                organization_id=organization_id,
            )
            if company:
                return [company]

            # --- ten sam numer z prefiksem kraju lub bez (DE123456789 ↔ 123456789) ---
            company = self._match_by_digits(uow=uow, organization_id=organization_id, normalized=normalized)
            if company:
                return [company]

        # --- fallback tylko dla placeholderów (TMP-/AI-/OTH-) ---
        if is_placeholder_identifier(input_.tax_number):
            company_dirty = uow.companies.get_by_tax_number(
                tax_number=input_.tax_number,
                organization_id=organization_id,
            )
            if company_dirty:
                return [company_dirty]

        return []

    @staticmethod
    def _match_by_digits(*, uow: UnitOfWork, organization_id: UUID, normalized: str) -> Company | None:
        """
        Numer zagraniczny zapisany kiedyś bez liter (albo odwrotnie) – porównuje same cyfry.
        Tylko gdy któraś strona ma litery i trafienie jest jednoznaczne; placeholdery pomija.
        """
        digits = re.sub(r"\D", "", normalized)
        input_has_letters = digits != normalized

        matches = [
            company
            for company in uow.companies.list_all(organization_id)
            if company.tax_number
            and company.tax_number != normalized
            and not is_placeholder_identifier(company.tax_number)
            and re.sub(r"\D", "", company.tax_number) == digits
            and (input_has_letters or re.search(r"[A-Za-z]", company.tax_number))
        ]
        return matches[0] if len(matches) == 1 else None
