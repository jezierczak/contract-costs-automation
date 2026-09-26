from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from contract_costs.repository.company_dashboard.dto.company_ledger_line_raw import CompanyLedgerLineRaw


class CompanyDashboardRepository(ABC):

    @abstractmethod
    def fetch_company_lines(
        self,
        *,
        organization_id: UUID,
        company_id: UUID,
        start: date,
        end: date,
    ) -> list[CompanyLedgerLineRaw]:
        """Linie firmy z okresu [start, end) — tylko filtrowanie, bez sum."""
        pass

    @abstractmethod
    def fetch_counterparty_lines(
            self,
            *,
            organization_id: UUID,
            counterparty_id: UUID,
            owner_company_id: UUID | None,
    ) -> list[CompanyLedgerLineRaw]:
        pass
