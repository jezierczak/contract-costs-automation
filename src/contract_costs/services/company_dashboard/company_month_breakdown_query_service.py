from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.common.pillars import Pillars
from contract_costs.services.company_dashboard.dto.company_month_breakdown_item import (
    CompanyMonthBreakdownItem,
)
from contract_costs.services.company_dashboard.dto.company_month_breakdown_query import (
    CompanyBreakdownQuery,
)
from contract_costs.services.company_dashboard.dto.month_breakdown_data import CompanyMonthBreakdownData
from contract_costs.services.company_dashboard.financials.company_financials import CompanyValueTypeFinancials
from contract_costs.services.company_dashboard.financials.company_financials_calculator import (
    CompanyFinancialsCalculator,
    period_range,
)
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

        start, end = period_range(action.year, action.month)

        lines = uow.company_dashboard.fetch_company_lines(
            organization_id=action.organization_id,
            company_id=action.company_id,
            start=start,
            end=end,
        )

        groups = CompanyFinancialsCalculator.breakdown(
            company_id=action.company_id,
            lines=lines,
        )

        cost_total = sum((g.financials.cost for g in groups), Pillars())
        revenue_total = sum((g.financials.revenue for g in groups), Pillars())

        costs = [
            self._item(g, g.financials.cost, cost_total)
            for g in groups
            if g.financials.cost != Pillars()
        ]
        revenues = [
            self._item(g, g.financials.revenue, revenue_total)
            for g in groups
            if g.financials.revenue != Pillars()
        ]

        costs.sort(key=lambda i: i.pillars.cashflow, reverse=True)
        revenues.sort(key=lambda i: i.pillars.cashflow, reverse=True)

        return CompanyMonthBreakdownData(
            costs=costs,
            revenues=revenues,
            cost_total=cost_total,
            revenue_total=revenue_total,
        )

    @staticmethod
    def _item(
        group: CompanyValueTypeFinancials,
        pillars: Pillars,
        total: Pillars,
    ) -> CompanyMonthBreakdownItem:
        return CompanyMonthBreakdownItem(
            code=group.code,
            name=group.name,
            is_fixed=group.is_fixed,
            pillars=pillars,
            share=pillars.cashflow / total.cashflow if total.cashflow else None,
        )
