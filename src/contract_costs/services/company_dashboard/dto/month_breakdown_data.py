from dataclasses import dataclass

from contract_costs.services.common.pillars import Pillars

from .company_month_breakdown_item import CompanyMonthBreakdownItem


@dataclass(slots=True)
class CompanyMonthBreakdownData:

    costs: list[CompanyMonthBreakdownItem]
    revenues: list[CompanyMonthBreakdownItem]

    cost_total: Pillars
    revenue_total: Pillars
