from dataclasses import dataclass

from contract_costs.services.company_dashboard.financials.company_financials import CompanyPeriodFinancials


@dataclass(slots=True)
class CompanyDashboardMonth:
    month: int
    label: str
    period: CompanyPeriodFinancials
