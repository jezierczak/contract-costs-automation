from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.repository.company_dashboard.company_dashboard_raw_data import CompanyDashboardRawData
from contract_costs.repository.company_dashboard.company_fixed_cost_raw import CompanyFixedCostRaw
from contract_costs.repository.company_dashboard.company_month_breakdown_raw import CompanyMonthBreakdownRaw


class CompanyDashboardRepository(ABC):

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