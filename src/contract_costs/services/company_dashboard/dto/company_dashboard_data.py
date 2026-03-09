from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.services.company_dashboard.dto.company_dashboard_month import CompanyDashboardMonth


@dataclass(slots=True)
class CompanyDashboardData:

    owner_companies: list[Company]
    selected_company_id: UUID

    year: int

    # YEAR
    year_revenue: Decimal = Decimal("0")
    year_costs: Decimal = Decimal("0")
    year_profit: Decimal = Decimal("0")

    year_non_deductible: Decimal = Decimal("0")
    year_cashflow: Decimal = Decimal("0")

    year_fixed_costs: Decimal = Decimal("0")

    # CURRENT MONTH
    current_month: CompanyDashboardMonth | None = None

    # PREVIOUS MONTHS
    previous_months: list[CompanyDashboardMonth] = field(default_factory=list)