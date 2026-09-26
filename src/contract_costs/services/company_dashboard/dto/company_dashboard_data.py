from dataclasses import dataclass, field
from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.services.company_dashboard.dto.company_dashboard_month import CompanyDashboardMonth
from contract_costs.services.company_dashboard.financials.company_financials import CompanyFinancials


@dataclass(slots=True)
class CompanyDashboardData:

    owner_companies: list[Company]
    selected_company_id: UUID

    year: int

    financials: CompanyFinancials

    # miesiące z danymi, od najnowszego
    months: list[CompanyDashboardMonth] = field(default_factory=list)
