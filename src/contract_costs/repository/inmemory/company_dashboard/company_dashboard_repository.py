from datetime import date
from uuid import UUID

from contract_costs.repository.company_dashboard.company_dashboard_repository import (
    CompanyDashboardRepository,
)
from contract_costs.repository.company_dashboard.dto.company_ledger_line_raw import CompanyLedgerLineRaw


class InMemoryCompanyDashboardRepository(CompanyDashboardRepository):
    """Odpowiednik widoku financial_ledger podawany wprost jako gotowe linie."""

    def __init__(
        self,
        company_lines: list[tuple[UUID, CompanyLedgerLineRaw]] | None = None,
    ) -> None:
        # (organization_id, linia)
        self._company_lines = company_lines or []

    def fetch_company_lines(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            start: date,
            end: date,
    ) -> list[CompanyLedgerLineRaw]:
        company = str(company_id)
        return [
            line
            for org_id, line in self._company_lines
            if org_id == organization_id
            and start <= line.record_date < end
            and line.status != "deleted"
            and (
                str(line.buyer_id) == company
                or str(line.seller_id) == company
                or (line.contract_type == "system" and str(line.contract_owner_id) == company)
            )
        ]

    def fetch_counterparty_lines(
            self,
            *,
            organization_id: UUID,
            counterparty_id: UUID,
            owner_company_id: UUID | None,
    ) -> list[CompanyLedgerLineRaw]:
        counterparty = str(counterparty_id)
        owner = str(owner_company_id) if owner_company_id else None
        return [
            line
            for org_id, line in self._company_lines
            if org_id == organization_id
            and line.status != "deleted"
            and counterparty in (str(line.buyer_id), str(line.seller_id))
            and (owner is None or owner in (str(line.buyer_id), str(line.seller_id)))
        ]
