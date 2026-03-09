from dataclasses import dataclass
from decimal import Decimal

from .company_month_breakdown_item import CompanyMonthBreakdownItem


@dataclass(slots=True)
class CompanyMonthBreakdownData:

    costs: list[CompanyMonthBreakdownItem]
    revenues: list[CompanyMonthBreakdownItem]

    cost_total: Decimal
    revenue_total: Decimal