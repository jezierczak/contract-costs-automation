from datetime import date
from decimal import Decimal
from uuid import UUID

import pytest

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.contracts.financials.contract_financials import IndicatorLevel
from contract_costs.services.contracts.financials.contract_financials_calculator import (
    ContractFinancialsCalculator,
)
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder

TODAY = date(2026, 6, 30)
COST_VT = new_uuid()
REVENUE_VT = new_uuid()
INTERNAL_VT = new_uuid()
DIRECTIONS = {
    COST_VT: ValueDirection.COST,
    REVENUE_VT: ValueDirection.REVENUE,
    INTERNAL_VT: ValueDirection.INTERNAL,
}


def _node(
    *,
    code: str,
    parent: ContractNode | None = None,
    budget: str | None = None,
    progress: dict[date, str] | None = None,
) -> ContractNode:
    return ContractNode(
        id=new_uuid(),
        organization_id=new_uuid(),
        contract_id=new_uuid(),
        parent_id=parent.id if parent else None,
        code=code,
        name=code,
        budget=Decimal(budget) if budget is not None else None,
        quantity=None,
        unit=None,
        is_active=True,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        progress_history={d: Decimal(p) for d, p in (progress or {}).items()},
    )


def _line(
    *,
    value_type_id: UUID,
    value: str,
    node: ContractNode | None = None,
    input_type: AmountInputType = AmountInputType.NET,
    tax_treatment: TaxTreatment = TaxTreatment.TAX_DEDUCTIBLE,
):
    builder = (
        FinancialRecordLineBuilder()
        .with_value_type_id(value_type_id)
        .with_amount(
            Amount.from_input(
                value=Decimal(value),
                input_type=input_type,
                vat_rate=VatRate.VAT_23,
                tax_treatment=tax_treatment,
            )
        )
    )
    if node is not None:
        builder = builder.with_contract_node_id(node.id)
    return builder.build()


def _calculate(nodes, lines, *, start=None, end=None, at_date=None):
    return ContractFinancialsCalculator.calculate(
        nodes=nodes,
        lines=lines,
        value_type_directions=DIRECTIONS,
        start_date=start,
        end_date=end,
        today=TODAY,
        at_date=at_date,
    )


# ---------------------------------------------------------------
# budżet i postęp
# ---------------------------------------------------------------

def test_budget_and_progress_roll_up_weighted_by_budget():
    root = _node(code="ROOT")
    a = _node(code="A", parent=root, budget="100", progress={TODAY: "0.5"})
    b = _node(code="B", parent=root, budget="300", progress={TODAY: "1.0"})

    result = _calculate([root, a, b], [])

    assert result.total.budget == Decimal("400")
    assert result.total.progress == Decimal("0.875")
    assert result.nodes[root.id].progress == Decimal("0.875")
    assert result.total.executed == Decimal("350")


def test_leaf_without_progress_counts_as_zero():
    root = _node(code="ROOT")
    a = _node(code="A", parent=root, budget="100", progress={TODAY: "1.0"})
    b = _node(code="B", parent=root, budget="100")

    result = _calculate([root, a, b], [])

    assert result.total.progress == Decimal("0.5")


def test_progress_is_none_when_nobody_entered_it():
    root = _node(code="ROOT")
    a = _node(code="A", parent=root, budget="100")

    result = _calculate([root, a], [])

    assert result.total.progress is None
    assert result.total.executed is None
    assert result.total.result_on_progress is None
    assert result.indicators.cost is None


def test_multiple_roots_are_summed():
    r1 = _node(code="R1", budget="100", progress={TODAY: "1.0"})
    r2 = _node(code="R2", budget="100", progress={TODAY: "0.0"})

    result = _calculate([r1, r2], [])

    assert result.total.budget == Decimal("200")
    assert result.total.progress == Decimal("0.5")


def test_progress_at_date_uses_history():
    a = _node(
        code="A",
        budget="100",
        progress={date(2026, 1, 31): "0.2", date(2026, 3, 31): "0.6"},
    )

    result = _calculate([a], [], at_date=date(2026, 2, 28))

    assert result.total.progress == Decimal("0.2")


# ---------------------------------------------------------------
# filary kwot
# ---------------------------------------------------------------

def test_pillars_come_from_amount():
    a = _node(code="A", budget="1000", progress={TODAY: "0.5"})
    lines = [
        # wpisane brutto — cashflow i net liczone z netto
        _line(value_type_id=COST_VT, value="123", node=a, input_type=AmountInputType.GROSS),
        _line(value_type_id=COST_VT, value="50", node=a, tax_treatment=TaxTreatment.NON_DEDUCTIBLE),
        _line(value_type_id=COST_VT, value="30", node=a, tax_treatment=TaxTreatment.NON_CASH_COST),
        _line(value_type_id=REVENUE_VT, value="400", node=a),
    ]

    result = _calculate([a], lines)
    cost = result.total.cost

    assert cost.net == Decimal("130.00")       # 100 + 30 amortyzacji
    assert cost.non_tax == Decimal("50")
    assert cost.cashflow == Decimal("150.00")  # 100 + 50, bez amortyzacji
    assert result.total.revenue.net == Decimal("400")
    assert result.total.result_net == Decimal("270.00")
    assert result.total.result_cashflow == Decimal("250.00")


def test_internal_lines_are_ignored():
    a = _node(code="A", budget="100", progress={TODAY: "0.5"})
    lines = [_line(value_type_id=INTERNAL_VT, value="999", node=a)]

    result = _calculate([a], lines)

    assert result.total.cost.cashflow == 0
    assert result.total.revenue.cashflow == 0


def test_lines_without_node_count_only_for_contract_total():
    root = _node(code="ROOT")
    a = _node(code="A", parent=root, budget="100")
    lines = [
        _line(value_type_id=COST_VT, value="10", node=a),
        _line(value_type_id=COST_VT, value="5"),
    ]

    result = _calculate([root, a], lines)

    assert result.nodes[root.id].cost.cashflow == Decimal("10")
    assert result.total.cost.cashflow == Decimal("15")


# ---------------------------------------------------------------
# wynik na postępie i prognoza
# ---------------------------------------------------------------

def test_result_on_progress_and_forecast():
    # przykład z planu: budżet 1 mln, postęp 40%, koszty 450 tys.
    a = _node(code="A", budget="1000000", progress={TODAY: "0.4"})
    lines = [_line(value_type_id=COST_VT, value="450000", node=a)]

    total = _calculate([a], lines).total

    assert total.executed == Decimal("400000")
    assert total.result_on_progress == Decimal("-50000")
    assert total.forecast_total_cost == Decimal("1125000")
    assert total.forecast_result == Decimal("-125000")


def test_forecast_hidden_below_minimum_progress():
    a = _node(code="A", budget="1000", progress={TODAY: "0.04"})
    lines = [_line(value_type_id=COST_VT, value="100", node=a)]

    total = _calculate([a], lines).total

    assert total.forecast_total_cost is None
    assert total.forecast_result is None


def test_billing_gap_negative_when_underbilled():
    a = _node(code="A", budget="1000", progress={TODAY: "0.5"})
    lines = [_line(value_type_id=REVENUE_VT, value="300", node=a)]

    assert _calculate([a], lines).total.billing_gap == Decimal("-200")


# ---------------------------------------------------------------
# wskaźniki
# ---------------------------------------------------------------

@pytest.mark.parametrize(
    "cost, expected",
    [
        ("500", IndicatorLevel.GREEN),   # koszt = wykonane
        ("525", IndicatorLevel.YELLOW),  # +5%
        ("526", IndicatorLevel.RED),
    ],
)
def test_cost_indicator(cost, expected):
    a = _node(code="A", budget="1000", progress={TODAY: "0.5"})
    lines = [_line(value_type_id=COST_VT, value=cost, node=a)]

    assert _calculate([a], lines).indicators.cost == expected


@pytest.mark.parametrize(
    "progress, expected",
    [
        ("0.5", IndicatorLevel.GREEN),   # czas 50%
        ("0.4", IndicatorLevel.YELLOW),  # 10 pp za czasem
        ("0.39", IndicatorLevel.RED),
    ],
)
def test_schedule_indicator(progress, expected):
    a = _node(code="A", budget="1000", progress={TODAY: progress})

    result = _calculate([a], [], start=date(2026, 1, 1), end=date(2026, 12, 27))

    assert result.indicators.time_progress == Decimal("0.5")
    assert result.indicators.schedule == expected


def test_schedule_indicator_needs_dates():
    a = _node(code="A", budget="1000", progress={TODAY: "0.5"})

    assert _calculate([a], []).indicators.schedule is None


@pytest.mark.parametrize(
    "revenue, expected",
    [
        ("450", IndicatorLevel.GREEN),   # niedofakturowane 5% budżetu
        ("400", IndicatorLevel.YELLOW),  # 10%
        ("399", IndicatorLevel.RED),
    ],
)
def test_billing_indicator(revenue, expected):
    a = _node(code="A", budget="1000", progress={TODAY: "0.5"})
    lines = [_line(value_type_id=REVENUE_VT, value=revenue, node=a)]

    assert _calculate([a], lines).indicators.billing == expected


def test_progress_stale_after_30_days():
    fresh = _node(code="A", budget="100", progress={date(2026, 5, 31): "0.5"})
    stale = _node(code="B", budget="100", progress={date(2026, 5, 30): "0.5"})

    assert _calculate([fresh], []).indicators.progress_stale is False
    assert _calculate([stale], []).indicators.progress_stale is True
    assert _calculate([stale], []).indicators.last_progress_date == date(2026, 5, 30)


def test_progress_stale_is_none_without_progress():
    a = _node(code="A", budget="100")

    assert _calculate([a], []).indicators.progress_stale is None
