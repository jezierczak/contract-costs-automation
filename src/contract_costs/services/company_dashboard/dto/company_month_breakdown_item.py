from dataclasses import dataclass
from decimal import Decimal


@dataclass(slots=True)
class CompanyMonthBreakdownItem:

    code: str | None
    name: str | None

    revenue: Decimal
    costs: Decimal
    non_deductible: Decimal

    total: Decimal
    percent_of_direction: Decimal