from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.contract_node import ContractNode
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.contracts.financials.contract_timeline import ContractTimelineCalculator
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder

TODAY = date(2026, 4, 15)
COST_VT = new_uuid()
REVENUE_VT = new_uuid()
INTERNAL_VT = new_uuid()
DIRECTIONS = {
    COST_VT: ValueDirection.COST,
    REVENUE_VT: ValueDirection.REVENUE,
    INTERNAL_VT: ValueDirection.INTERNAL,
}


def _node(*, budget: str, progress: dict[date, str] | None = None) -> ContractNode:
    return ContractNode(
        id=new_uuid(),
        organization_id=new_uuid(),
        contract_id=new_uuid(),
        parent_id=None,
        code="A",
        name="A",
        budget=Decimal(budget),
        quantity=None,
        unit=None,
        is_active=True,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        progress_history={d: Decimal(p) for d, p in (progress or {}).items()},
    )


def _line(*, value_type_id: UUID, value: str, record_id: UUID | None, tax_treatment=TaxTreatment.TAX_DEDUCTIBLE):
    builder = (
        FinancialRecordLineBuilder()
        .with_value_type_id(value_type_id)
        .with_amount(
            Amount.from_input(
                value=Decimal(value),
                input_type=AmountInputType.NET,
                vat_rate=VatRate.VAT_23,
                tax_treatment=tax_treatment,
            )
        )
    )
    if record_id is not None:
        builder = builder.with_financial_record_id(record_id)
    return builder.build()


def _calculate(nodes, lines, record_dates, *, start=None, end=None, today=TODAY):
    return ContractTimelineCalculator.calculate(
        nodes=nodes,
        lines=lines,
        record_dates=record_dates,
        value_type_directions=DIRECTIONS,
        start_date=start,
        end_date=end,
        today=today,
    )


def test_months_group_lines_by_record_date_and_accumulate():
    jan, mar = new_uuid(), new_uuid()
    lines = [
        _line(value_type_id=COST_VT, value="100", record_id=jan),
        _line(value_type_id=COST_VT, value="30", record_id=jan, tax_treatment=TaxTreatment.NON_CASH_COST),
        _line(value_type_id=COST_VT, value="50", record_id=mar),
        _line(value_type_id=REVENUE_VT, value="200", record_id=mar),
    ]
    dates = {jan: date(2026, 1, 10), mar: date(2026, 3, 5)}

    timeline = _calculate([], lines, dates)

    assert [(m.year, m.month) for m in timeline.months] == [(2026, 1), (2026, 2), (2026, 3), (2026, 4)]

    january, february, march, april = timeline.months
    assert january.cost.net == Decimal("130")
    assert january.cost.cashflow == Decimal("100")
    assert february.cost.cashflow == 0
    assert february.cumulative_cost.cashflow == Decimal("100")
    assert march.revenue.net == Decimal("200")
    assert april.cumulative_cost.cashflow == Decimal("150")
    assert april.cumulative_revenue.cashflow == Decimal("200")


def test_executed_cumulative_uses_progress_at_month_end():
    node = _node(budget="1000", progress={date(2026, 1, 31): "0.1", date(2026, 3, 15): "0.4"})
    record = new_uuid()
    lines = [_line(value_type_id=COST_VT, value="150", record_id=record)]

    timeline = _calculate([node], lines, {record: date(2026, 2, 1)})
    by_month = {(m.year, m.month): m for m in timeline.months}

    assert by_month[(2026, 1)].executed_cumulative == Decimal("100")
    assert by_month[(2026, 2)].executed_cumulative == Decimal("100")
    assert by_month[(2026, 3)].executed_cumulative == Decimal("400")
    # luty: wykonane 100, koszty narastająco 150
    assert by_month[(2026, 2)].result_on_progress_cumulative == Decimal("-50")


def test_executed_cumulative_is_none_before_any_progress():
    node = _node(budget="1000", progress={date(2026, 3, 1): "0.5"})

    timeline = _calculate([node], [], {}, start=date(2026, 1, 1))

    assert timeline.months[0].executed_cumulative is None
    assert timeline.months[0].result_on_progress_cumulative is None


def test_range_starts_at_contract_start_and_stops_at_contract_end():
    record = new_uuid()
    lines = [_line(value_type_id=COST_VT, value="10", record_id=record)]

    timeline = _calculate(
        [],
        lines,
        {record: date(2026, 2, 10)},
        start=date(2025, 12, 1),
        end=date(2026, 3, 31),
        today=date(2026, 9, 1),
    )

    assert [(m.year, m.month) for m in timeline.months] == [
        (2025, 12), (2026, 1), (2026, 2), (2026, 3),
    ]


def test_future_contract_without_data_does_not_backfill_to_today():
    timeline = _calculate([], [], {}, start=date(2026, 6, 1), today=date(2026, 4, 15))

    assert [(m.year, m.month) for m in timeline.months] == [(2026, 6)]


def test_empty_contract_has_no_months():
    assert _calculate([], [], {}).months == []


def test_lines_without_record_date_go_to_undated():
    record = new_uuid()
    lines = [
        _line(value_type_id=COST_VT, value="10", record_id=None),
        _line(value_type_id=REVENUE_VT, value="20", record_id=record),
    ]

    timeline = _calculate([], lines, {record: None})

    assert timeline.months == []
    assert timeline.undated_cost.cashflow == Decimal("10")
    assert timeline.undated_revenue.cashflow == Decimal("20")


def test_internal_lines_are_ignored():
    record = new_uuid()
    lines = [_line(value_type_id=INTERNAL_VT, value="999", record_id=record)]

    timeline = _calculate([], lines, {record: date(2026, 4, 1)})

    assert timeline.months == []
