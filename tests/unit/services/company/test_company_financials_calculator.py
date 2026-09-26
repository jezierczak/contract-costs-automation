from datetime import date
from decimal import Decimal

from contract_costs.common.ids import new_uuid
from contract_costs.repository.company_dashboard.dto.company_ledger_line_raw import CompanyLedgerLineRaw
from contract_costs.services.company_dashboard.financials.company_financials_calculator import (
    CompanyFinancialsCalculator,
)

YEAR = 2026
COMPANY = new_uuid()
OTHER_OWN = new_uuid()
SUPPLIER = new_uuid()
CLIENT = new_uuid()


def _line(
    *,
    buyer,
    seller,
    value: str,
    direction: str = "COST",
    input_type: str = "net",
    vat: str = "0.23",
    tax: str = "tax_deductible",
    month: int = 3,
    value_type_id: str = "vt-cost",
    contract_type: str | None = None,
    contract_owner=None,
) -> CompanyLedgerLineRaw:
    return CompanyLedgerLineRaw(
        record_id=str(new_uuid()),
        record_date=date(YEAR, month, 10),
        buyer_id=str(buyer),
        seller_id=str(seller),
        direction=direction,
        contract_type=contract_type,
        contract_owner_id=str(contract_owner) if contract_owner else None,
        value_type_id=value_type_id,
        value_type_code=value_type_id.upper(),
        value_type_name=value_type_id,
        item_name="item",
        description=None,
        amount_value=Decimal(value),
        amount_input_type=input_type,
        vat_rate=Decimal(vat),
        tax_treatment=tax,
    )


def _calc(lines):
    return CompanyFinancialsCalculator.calculate(year=YEAR, company_id=COMPANY, lines=lines)


def test_gross_cost_counts_as_net_in_every_pillar():
    total = _calc([_line(buyer=COMPANY, seller=SUPPLIER, value="123.00", input_type="gross")]).total

    assert total.cost.net == Decimal("100.00")
    assert total.cost.cashflow == Decimal("100.00")


def test_depreciation_is_tax_cost_without_cashflow():
    total = _calc([_line(buyer=COMPANY, seller=SUPPLIER, value="500.00", tax="non_cash_cost")]).total

    assert total.cost.net == Decimal("500.00")
    assert total.cost.cashflow == Decimal("0.00")
    assert total.result_net == Decimal("-500.00")
    assert total.result_cashflow == Decimal("0.00")


def test_non_deductible_is_cashflow_but_not_tax_cost():
    total = _calc([_line(buyer=COMPANY, seller=SUPPLIER, value="80.00", tax="non_deductible")]).total

    assert total.cost.net == Decimal("0.00")
    assert total.cost.non_tax == Decimal("80.00")
    assert total.cost.cashflow == Decimal("80.00")


def test_result_can_be_negative():
    total = _calc([
        _line(buyer=CLIENT, seller=COMPANY, value="1000.00", direction="REVENUE"),
        _line(buyer=COMPANY, seller=SUPPLIER, value="1500.00"),
    ]).total

    assert total.revenue.cashflow == Decimal("1000.00")
    assert total.result_net == Decimal("-500.00")
    assert total.result_cashflow == Decimal("-500.00")


def test_fixed_costs_are_part_of_costs_and_tracked_separately():
    total = _calc([
        _line(buyer=COMPANY, seller=SUPPLIER, value="300.00", direction="FIXED", tax="non_deductible"),
        _line(buyer=COMPANY, seller=SUPPLIER, value="200.00"),
    ]).total

    assert total.fixed.cashflow == Decimal("300.00")
    assert total.cost.cashflow == Decimal("500.00")


def test_legacy_system_contract_counts_as_fixed_cost():
    total = _calc([
        _line(buyer=COMPANY, seller=SUPPLIER, value="50.00", contract_type="system", contract_owner=COMPANY),
    ]).total

    assert total.fixed.cashflow == Decimal("50.00")
    assert total.cost.cashflow == Decimal("50.00")


def test_fixed_sale_is_revenue_of_seller():
    total = _calc([
        _line(buyer=OTHER_OWN, seller=COMPANY, value="100.00", direction="FIXED"),
    ]).total

    assert total.revenue.cashflow == Decimal("100.00")
    assert total.fixed.cashflow == Decimal("0")


def test_internal_side_follows_role_on_invoice():
    total = _calc([
        _line(buyer=OTHER_OWN, seller=COMPANY, value="400.00", direction="INTERNAL"),
        _line(buyer=COMPANY, seller=OTHER_OWN, value="150.00", direction="INTERNAL"),
    ]).total

    assert total.revenue.cashflow == Decimal("400.00")
    assert total.cost.cashflow == Decimal("150.00")


def test_lines_of_other_companies_are_ignored():
    total = _calc([_line(buyer=OTHER_OWN, seller=SUPPLIER, value="999.00")]).total

    assert total.cost.cashflow == Decimal("0")
    assert total.revenue.cashflow == Decimal("0")


def test_months_sum_to_total():
    fin = _calc([
        _line(buyer=COMPANY, seller=SUPPLIER, value="10.00", month=1),
        _line(buyer=COMPANY, seller=SUPPLIER, value="20.00", month=1),
        _line(buyer=CLIENT, seller=COMPANY, value="70.00", direction="REVENUE", month=2),
    ])

    assert sorted(fin.months) == [1, 2]
    assert fin.months[1].cost.cashflow == Decimal("30.00")
    assert fin.months[2].revenue.cashflow == Decimal("70.00")
    assert sum((p.result_cashflow for p in fin.months.values()), Decimal("0")) == fin.total.result_cashflow


def test_breakdown_groups_by_value_type():
    items = CompanyFinancialsCalculator.breakdown(
        company_id=COMPANY,
        lines=[
            _line(buyer=COMPANY, seller=SUPPLIER, value="10.00", value_type_id="vt-a"),
            _line(buyer=COMPANY, seller=SUPPLIER, value="15.00", value_type_id="vt-a"),
            _line(buyer=COMPANY, seller=SUPPLIER, value="40.00", value_type_id="vt-zus", direction="FIXED"),
        ],
    )

    by_id = {i.value_type_id: i for i in items}
    assert by_id["vt-a"].financials.cost.cashflow == Decimal("25.00")
    assert by_id["vt-a"].is_fixed is False
    assert by_id["vt-zus"].is_fixed is True
