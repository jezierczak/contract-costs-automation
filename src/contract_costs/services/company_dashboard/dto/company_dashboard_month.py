from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class CompanyDashboardMonth:
    month: int
    label: str

    revenue: Decimal = Decimal("0")
    costs: Decimal = Decimal("0")
    profit: Decimal = Decimal("0")

    non_deductible: Decimal = Decimal("0")

    cashflow: Decimal = Decimal("0")

    fixed_costs: Decimal = Decimal("0")