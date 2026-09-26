from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from contract_costs.repository.company_dashboard.dto.company_dashboard_raw_data import CompanyDashboardRawData
from contract_costs.repository.company_dashboard.dto.company_fixed_cost_raw import CompanyFixedCostRaw
from contract_costs.repository.company_dashboard.dto.company_ledger_line_raw import CompanyLedgerLineRaw
from contract_costs.repository.company_dashboard.dto.company_month_breakdown_raw import CompanyMonthBreakdownRaw
from contract_costs.repository.company_dashboard.dto.counterparty_ledger_line_raw import CounterpartyLedgerLineRaw
from contract_costs.repository.company_dashboard.dto.counterparty_summary_raw import CounterpartySummaryRaw
from contract_costs.repository.company_dashboard.dto.counterparty_year_raw import CounterpartyYearRaw


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
    def fetch_dashboard_data(
        self,
        *,
        organization_id: UUID,
        company_id: UUID,
        year: int,
    ) -> CompanyDashboardRawData:
        pass

    @abstractmethod
    def fetch_month_breakdown(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            year: int,
            month: int,
    ) -> list[CompanyMonthBreakdownRaw]:
        pass

    @abstractmethod
    def fetch_fixed_costs(
            self,
            *,
            organization_id: UUID,
            company_id: UUID,
            year: int,
            month: int | None,
    ) -> list[CompanyFixedCostRaw]:
        pass

    @abstractmethod
    def fetch_counterparty_lines(
            self,
            *,
            organization_id: UUID,
            counterparty_id: UUID,
            owner_company_id: UUID | None,
    ) -> list[CounterpartyLedgerLineRaw]:
        pass

