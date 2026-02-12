from decimal import Decimal

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now

from contract_costs.model.financial_record_line import FinancialRecordLine
from contract_costs.model.amount import Amount, VatRate, TaxTreatment


def build_line(
    *,
    quantity=Decimal("1"),
    amount_value=Decimal("100.00"),
):
    return FinancialRecordLine(
        id=new_uuid(),
        organization_id=new_uuid(),
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        financial_record_id=new_uuid(),
        contract_id=None,
        contract_node_id=None,
        value_type_id=None,
        item_name="Service",
        quantity=quantity,
        unit=None,
        amount=Amount(
            value=amount_value,
            vat_rate=VatRate.VAT_23,
            tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
        ),
        description=None,
    )

def test_financial_record_line_creation():
    line = build_line()

    assert line.item_name == "Service"
    assert line.amount.value == Decimal("100.00")
    assert line.quantity == Decimal("1")


def test_financial_record_line_amount_calculation():
    line = build_line(amount_value=Decimal("100.00"))

    assert line.amount.tax == Decimal("23.00")
    assert line.amount.gross == Decimal("123.00")

def test_financial_record_line_is_mutable():
    line = build_line()

    line.item_name = "Updated Service"

    assert line.item_name == "Updated Service"

import pytest

def test_financial_record_line_disallows_dynamic_attributes():
    line = build_line()

    with pytest.raises(AttributeError):
        line.random_field = 123

def test_financial_record_line_can_link_to_contract():
    contract_id = new_uuid()

    line = build_line()
    line.contract_id = contract_id

    assert line.contract_id == contract_id
