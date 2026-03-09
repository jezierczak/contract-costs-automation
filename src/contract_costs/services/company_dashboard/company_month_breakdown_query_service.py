from decimal import Decimal

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.company_dashboard.dto.company_month_breakdown_query import (
    CompanyBreakdownQuery,
)
from contract_costs.services.company_dashboard.dto.company_month_breakdown_item import (
    CompanyMonthBreakdownItem,
)
from contract_costs.services.company_dashboard.dto.month_breakdown_data import CompanyMonthBreakdownData

from contract_costs.unit_of_work import UnitOfWork


class CompanyMonthBreakdownQueryService(
    ActionHandler[CompanyBreakdownQuery, CompanyMonthBreakdownData]
):

    def execute(
        self,
        *,
        action: CompanyBreakdownQuery,
        uow: UnitOfWork,
    ) -> CompanyMonthBreakdownData:

        repo = uow.company_dashboard

        raw_items = repo.fetch_month_breakdown(
            organization_id=action.organization_id,
            company_id=action.company_id,
            year=action.year,
            month=action.month,
        )

        costs: list[CompanyMonthBreakdownItem] = []
        revenues: list[CompanyMonthBreakdownItem] = []

        cost_total = Decimal("0")
        revenue_total = Decimal("0")

        for r in raw_items:

            total = r.costs + r.non_deductible + r.revenue

            item = CompanyMonthBreakdownItem(
                code=r.code,
                name=r.name,
                revenue=r.revenue,
                costs=r.costs,
                non_deductible=r.non_deductible,
                total=total,
                percent_of_direction=Decimal("0"),
            )

            if r.revenue > 0:
                revenues.append(item)
                revenue_total += total
            else:
                costs.append(item)
                cost_total += total

        # procenty

        for i in costs:
            if cost_total > 0:
                i.percent_of_direction = (i.total / cost_total) * 100

        for i in revenues:
            if revenue_total > 0:
                i.percent_of_direction = (i.total / revenue_total) * 100

        return CompanyMonthBreakdownData(
            costs=costs,
            revenues=revenues,
            cost_total=cost_total,
            revenue_total=revenue_total,
        )