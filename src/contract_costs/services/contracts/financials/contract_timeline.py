import calendar
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable
from uuid import UUID

from contract_costs.model.contract_node import ContractNode
from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.contracts.financials.contract_financials import Pillars
from contract_costs.services.contracts.financials.contract_financials_calculator import (
    ContractFinancialsCalculator,
)


@dataclass(frozen=True)
class ContractMonth:
    year: int
    month: int
    cost: Pillars
    revenue: Pillars
    cumulative_cost: Pillars
    cumulative_revenue: Pillars
    # budżet × postęp obowiązujący na koniec miesiąca
    executed_cumulative: Decimal | None

    @property
    def result_on_progress_cumulative(self) -> Decimal | None:
        if self.executed_cumulative is None:
            return None
        return self.executed_cumulative - self.cumulative_cost.cashflow


@dataclass(frozen=True)
class ContractTimeline:
    months: list[ContractMonth]
    # linie, których rekord nie ma daty — nie trafiają do żadnego miesiąca
    undated_cost: Pillars
    undated_revenue: Pillars


class ContractTimelineCalculator:
    """Koszty i przychody kontraktu po miesiącach + wykonane narastająco (krzywa S)."""

    @classmethod
    def calculate(
        cls,
        *,
        nodes: Iterable[ContractNode],
        lines: Iterable[FinancialRecordLine],
        record_dates: dict[UUID, date | None],
        value_type_directions: dict[UUID, ValueDirection],
        start_date: date | None,
        end_date: date | None,
        today: date,
    ) -> ContractTimeline:

        nodes = list(nodes)
        monthly_cost: dict[tuple[int, int], Pillars] = {}
        monthly_revenue: dict[tuple[int, int], Pillars] = {}
        undated_cost = Pillars()
        undated_revenue = Pillars()

        for line in lines:
            if line.amount is None or line.value_type_id is None:
                continue

            direction = value_type_directions.get(line.value_type_id)
            if direction not in (ValueDirection.COST, ValueDirection.REVENUE):
                continue

            pillars = Pillars.of(line.amount)
            record_date = (
                record_dates.get(line.financial_record_id)
                if line.financial_record_id
                else None
            )

            if record_date is None:
                if direction == ValueDirection.COST:
                    undated_cost += pillars
                else:
                    undated_revenue += pillars
                continue

            key = (record_date.year, record_date.month)
            bucket = monthly_cost if direction == ValueDirection.COST else monthly_revenue
            bucket[key] = bucket.get(key, Pillars()) + pillars

        month_keys = cls._month_range(
            data_months=set(monthly_cost) | set(monthly_revenue) | cls._progress_months(nodes),
            start_date=start_date,
            end_date=end_date,
            today=today,
        )

        months: list[ContractMonth] = []
        cumulative_cost = Pillars()
        cumulative_revenue = Pillars()

        for year, month in month_keys:
            cost = monthly_cost.get((year, month), Pillars())
            revenue = monthly_revenue.get((year, month), Pillars())
            cumulative_cost += cost
            cumulative_revenue += revenue

            month_end = date(year, month, calendar.monthrange(year, month)[1])
            executed = ContractFinancialsCalculator.calculate(
                nodes=nodes,
                lines=[],
                value_type_directions=value_type_directions,
                start_date=start_date,
                end_date=end_date,
                today=today,
                at_date=month_end,
            ).total.executed

            months.append(
                ContractMonth(
                    year=year,
                    month=month,
                    cost=cost,
                    revenue=revenue,
                    cumulative_cost=cumulative_cost,
                    cumulative_revenue=cumulative_revenue,
                    executed_cumulative=executed,
                )
            )

        return ContractTimeline(
            months=months,
            undated_cost=undated_cost,
            undated_revenue=undated_revenue,
        )

    @staticmethod
    def _progress_months(nodes: list[ContractNode]) -> set[tuple[int, int]]:
        return {(d.year, d.month) for n in nodes for d in n.progress_history}

    @staticmethod
    def _month_range(
        *,
        data_months: set[tuple[int, int]],
        start_date: date | None,
        end_date: date | None,
        today: date,
    ) -> list[tuple[int, int]]:
        """
        Od najwcześniejszego z: startu kontraktu / pierwszych danych
        do najpóźniejszego z: ostatnich danych / dziś (ale nie dalej niż koniec kontraktu).
        """
        bounds = set(data_months)
        if start_date:
            bounds.add((start_date.year, start_date.month))

        if not bounds:
            return []

        horizon = min(today, end_date) if end_date else today
        if (horizon.year, horizon.month) >= min(bounds):
            bounds.add((horizon.year, horizon.month))

        first, last = min(bounds), max(bounds)
        result: list[tuple[int, int]] = []
        year, month = first
        while (year, month) <= last:
            result.append((year, month))
            month += 1
            if month > 12:
                year, month = year + 1, 1
        return result
