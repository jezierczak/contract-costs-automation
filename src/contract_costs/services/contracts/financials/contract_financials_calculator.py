from datetime import date
from decimal import Decimal
from typing import Iterable
from uuid import UUID

from contract_costs.model.contract_node import ContractNode
from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.contracts.financials.contract_financials import (
    ZERO,
    ContractFinancials,
    ContractIndicators,
    IndicatorLevel,
    Pillars,
    ScopeFinancials,
)
from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex

# koszty: o ile koszty cashflow przekraczają wykonane (względem wykonanego)
COST_OVERRUN_YELLOW_UP_TO = Decimal("0.05")
# harmonogram: o ile punktów procentowych postęp zostaje za upływem czasu
SCHEDULE_LAG_YELLOW_UP_TO = Decimal("0.10")
# fakturowanie: niedofakturowanie jako część budżetu
UNDERBILLING_GREEN_UP_TO = Decimal("0.05")
UNDERBILLING_YELLOW_UP_TO = Decimal("0.10")
# postęp starszy niż tyle dni uznajemy za nieaktualny
PROGRESS_STALE_AFTER_DAYS = 30


class ContractFinancialsCalculator:
    """
    Jedno źródło prawdy dla finansów kontraktu (lista, szczegóły, dashboard).

    Kontrakt liczy tylko COST i REVENUE — INTERNAL celowo pomijamy
    (rozliczenia między firmami own są neutralne dla wyniku właściciela).
    """

    @classmethod
    def calculate(
        cls,
        *,
        nodes: Iterable[ContractNode],
        lines: Iterable[FinancialRecordLine],
        value_type_directions: dict[UUID, ValueDirection],
        start_date: date | None,
        end_date: date | None,
        today: date,
        at_date: date | None = None,
    ) -> ContractFinancials:

        tree = ContractNodeTreeIndex(list(nodes))
        reference_date = at_date or today

        node_cost, node_revenue, unassigned_cost, unassigned_revenue = cls._sum_lines(
            lines=lines,
            value_type_directions=value_type_directions,
            known_node_ids=set(tree.nodes_by_id),
        )

        node_financials = cls._rollup(
            tree=tree,
            node_cost=node_cost,
            node_revenue=node_revenue,
            at_date=at_date,
        )

        roots = [node_financials[r.id] for r in tree.roots()]
        total = ScopeFinancials(
            budget=sum((r.budget for r in roots), ZERO),
            progress=cls._weighted_progress(roots),
            cost=sum((r.cost for r in roots), unassigned_cost),
            revenue=sum((r.revenue for r in roots), unassigned_revenue),
        )

        indicators = cls._indicators(
            total=total,
            tree=tree,
            start_date=start_date,
            end_date=end_date,
            reference_date=reference_date,
        )

        return ContractFinancials(
            total=total,
            nodes=node_financials,
            indicators=indicators,
        )

    # =====================================================
    # LINES
    # =====================================================

    @staticmethod
    def _sum_lines(
        *,
        lines: Iterable[FinancialRecordLine],
        value_type_directions: dict[UUID, ValueDirection],
        known_node_ids: set[UUID],
    ) -> tuple[dict[UUID, Pillars], dict[UUID, Pillars], Pillars, Pillars]:

        node_cost: dict[UUID, Pillars] = {}
        node_revenue: dict[UUID, Pillars] = {}
        unassigned_cost = Pillars()
        unassigned_revenue = Pillars()

        for line in lines:
            if line.amount is None or line.value_type_id is None:
                continue

            direction = value_type_directions.get(line.value_type_id)
            if direction not in (ValueDirection.COST, ValueDirection.REVENUE):
                continue

            pillars = Pillars.of(line.amount)
            node_id = line.contract_node_id

            # linie bez węzła (lub z węzłem spoza drzewa) liczą się tylko do sumy kontraktu
            if node_id is None or node_id not in known_node_ids:
                if direction == ValueDirection.COST:
                    unassigned_cost += pillars
                else:
                    unassigned_revenue += pillars
                continue

            bucket = node_cost if direction == ValueDirection.COST else node_revenue
            bucket[node_id] = bucket.get(node_id, Pillars()) + pillars

        return node_cost, node_revenue, unassigned_cost, unassigned_revenue

    # =====================================================
    # TREE ROLLUP
    # =====================================================

    @classmethod
    def _rollup(
        cls,
        *,
        tree: ContractNodeTreeIndex,
        node_cost: dict[UUID, Pillars],
        node_revenue: dict[UUID, Pillars],
        at_date: date | None,
    ) -> dict[UUID, ScopeFinancials]:

        result: dict[UUID, ScopeFinancials] = {}

        for node in tree.postorder():
            own_cost = node_cost.get(node.id, Pillars())
            own_revenue = node_revenue.get(node.id, Pillars())

            if tree.is_leaf(node):
                result[node.id] = ScopeFinancials(
                    budget=node.budget or ZERO,
                    progress=node.progress_at(at_date) if at_date else node.progress,
                    cost=own_cost,
                    revenue=own_revenue,
                )
                continue

            children = [result[c.id] for c in tree.children_of(node.id)]
            result[node.id] = ScopeFinancials(
                budget=sum((c.budget for c in children), ZERO),
                progress=cls._weighted_progress(children),
                cost=sum((c.cost for c in children), own_cost),
                revenue=sum((c.revenue for c in children), own_revenue),
            )

        return result

    @staticmethod
    def _weighted_progress(scopes: list[ScopeFinancials]) -> Decimal | None:
        # zakres bez wpisanego postępu liczy się jako 0%;
        # None tylko wtedy, gdy postępu nie ma nigdzie
        if all(s.progress is None for s in scopes):
            return None

        total_budget = sum((s.budget for s in scopes), ZERO)
        if total_budget == 0:
            return None

        weighted = sum((s.budget * (s.progress or ZERO) for s in scopes), ZERO)
        return weighted / total_budget

    # =====================================================
    # INDICATORS
    # =====================================================

    @classmethod
    def _indicators(
        cls,
        *,
        total: ScopeFinancials,
        tree: ContractNodeTreeIndex,
        start_date: date | None,
        end_date: date | None,
        reference_date: date,
    ) -> ContractIndicators:

        time_progress = cls.time_progress(
            start_date=start_date,
            end_date=end_date,
            today=reference_date,
        )

        last_progress_date = max(
            (
                d
                for node in tree.all_nodes()
                for d in node.progress_history
                if d <= reference_date
            ),
            default=None,
        )
        progress_stale = (
            None
            if last_progress_date is None
            else (reference_date - last_progress_date).days > PROGRESS_STALE_AFTER_DAYS
        )

        return ContractIndicators(
            cost=cls._cost_level(total),
            schedule=cls._schedule_level(total.progress, time_progress),
            billing=cls._billing_level(total),
            time_progress=time_progress,
            last_progress_date=last_progress_date,
            progress_stale=progress_stale,
        )

    @staticmethod
    def _cost_level(total: ScopeFinancials) -> IndicatorLevel | None:
        executed = total.executed
        if not executed:
            return None

        overrun = (total.cost.cashflow - executed) / executed
        if overrun <= 0:
            return IndicatorLevel.GREEN
        if overrun <= COST_OVERRUN_YELLOW_UP_TO:
            return IndicatorLevel.YELLOW
        return IndicatorLevel.RED

    @staticmethod
    def _schedule_level(
        progress: Decimal | None,
        time_progress: Decimal | None,
    ) -> IndicatorLevel | None:
        if progress is None or time_progress is None:
            return None

        lag = time_progress - progress
        if lag <= 0:
            return IndicatorLevel.GREEN
        if lag <= SCHEDULE_LAG_YELLOW_UP_TO:
            return IndicatorLevel.YELLOW
        return IndicatorLevel.RED

    @staticmethod
    def _billing_level(total: ScopeFinancials) -> IndicatorLevel | None:
        gap = total.billing_gap
        if gap is None or not total.budget:
            return None

        underbilled = -gap / total.budget
        if underbilled <= UNDERBILLING_GREEN_UP_TO:
            return IndicatorLevel.GREEN
        if underbilled <= UNDERBILLING_YELLOW_UP_TO:
            return IndicatorLevel.YELLOW
        return IndicatorLevel.RED

    @staticmethod
    def time_progress(
        *,
        start_date: date | None,
        end_date: date | None,
        today: date,
    ) -> Decimal | None:
        if not start_date or not end_date:
            return None

        total_days = (end_date - start_date).days
        if total_days <= 0:
            return None

        elapsed_days = (today - start_date).days
        if elapsed_days <= 0:
            return ZERO
        if elapsed_days >= total_days:
            return Decimal("1")

        return Decimal(elapsed_days) / Decimal(total_days)
