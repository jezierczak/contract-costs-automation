from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class CompanyDashboardMonthRaw:

    month: int
    label: str

    revenue: Decimal
    costs: Decimal

    non_deductible: Decimal

    fixed_costs: Decimal