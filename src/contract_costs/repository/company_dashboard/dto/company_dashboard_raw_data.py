from dataclasses import dataclass
from decimal import Decimal

from contract_costs.repository.company_dashboard.dto.company_dashboard_month_raw import CompanyDashboardMonthRaw


@dataclass(slots=True)
class CompanyDashboardRawData:

    year_revenue: Decimal
    year_costs: Decimal

    year_non_deductible: Decimal

    year_fixed_costs: Decimal

    months: list[CompanyDashboardMonthRaw]