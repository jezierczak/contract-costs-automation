from decimal import Decimal
from contract_costs.model.amount import (
    Amount,
    VatRate,
    TaxTreatment,
    AmountInputType,
)


def test_tax_deductible_net_vat_23():
    amount = Amount(
        value=Decimal("100.00"),
        input_type=AmountInputType.NET,
        vat_rate=VatRate.VAT_23,
        tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
    )

    assert amount.net == Decimal("100.00")
    assert amount.tax == Decimal("23.00")
    assert amount.gross == Decimal("123.00")
    assert amount.non_tax_cost == Decimal("0.00")


def test_non_deductible_ignores_vat():
    amount = Amount(
        value=Decimal("100.00"),
        input_type=AmountInputType.NET,
        vat_rate=VatRate.VAT_23,
        tax_treatment=TaxTreatment.NON_DEDUCTIBLE,
    )

    assert amount.net == Decimal("0.00")
    assert amount.tax == Decimal("0.00")
    assert amount.gross == Decimal("100.00")
    assert amount.non_tax_cost == Decimal("100.00")


def test_vat_zw_has_no_tax():
    amount = Amount(
        value=Decimal("100.00"),
        input_type=AmountInputType.NET,
        vat_rate=VatRate.VAT_ZW,
        tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
    )

    assert amount.tax == Decimal("0.00")
    assert amount.gross == Decimal("100.00")


def test_from_input_net():
    amount = Amount.from_input(
        value=Decimal("100.00"),
        input_type=AmountInputType.NET,
        vat_rate=VatRate.VAT_23,
        tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
    )

    assert amount.net == Decimal("100.00")
    assert amount.tax == Decimal("23.00")


def test_from_input_gross():
    amount = Amount.from_input(
        value=Decimal("123.00"),
        input_type=AmountInputType.GROSS,
        vat_rate=VatRate.VAT_23,
        tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
    )

    assert amount.net == Decimal("100.00")
    assert amount.tax == Decimal("23.00")
    assert amount.gross == Decimal("123.00")

def test_from_input_gross_vat_zw():
    amount = Amount.from_input(
        value=Decimal("100.00"),
        input_type=AmountInputType.GROSS,
        vat_rate=VatRate.VAT_ZW,
        tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
    )

    assert amount.net == Decimal("100.00")
    assert amount.tax == Decimal("0.00")


def test_from_input_non_deductible_has_priority():
    amount = Amount.from_input(
        value=Decimal("123.00"),
        input_type=AmountInputType.GROSS,
        vat_rate=VatRate.VAT_23,
        tax_treatment=TaxTreatment.NON_DEDUCTIBLE,
    )

    assert amount.net == Decimal("0.00")
    assert amount.tax == Decimal("0.00")
    assert amount.gross == Decimal("123.00")
    assert amount.non_tax_cost == Decimal("123.00")


def test_net_or_zero_returns_zero_when_zero():
    amount = Amount(
        value=Decimal("100.00"),
        input_type=AmountInputType.NET,
        vat_rate=VatRate.VAT_23,
        tax_treatment=TaxTreatment.NON_DEDUCTIBLE,
    )

    assert amount.net_or_zero == Decimal("0.00")


# ---------------------------------------------------------------
# cashflow (analizy, netto) vs payable (płatności, brutto)
# ---------------------------------------------------------------

import pytest


@pytest.mark.parametrize(
    "value, input_type, tax_treatment, cashflow, payable",
    [
        # TAX_DEDUCTIBLE — cashflow zawsze netto, niezależnie od sposobu wpisania
        ("100.00", AmountInputType.NET, TaxTreatment.TAX_DEDUCTIBLE, "100.00", "123.00"),
        ("123.00", AmountInputType.GROSS, TaxTreatment.TAX_DEDUCTIBLE, "100.00", "123.00"),
        # NON_DEDUCTIBLE — cały wydatek jest przepływem, VAT się nie odlicza
        ("123.00", AmountInputType.NET, TaxTreatment.NON_DEDUCTIBLE, "123.00", "123.00"),
        ("123.00", AmountInputType.GROSS, TaxTreatment.NON_DEDUCTIBLE, "123.00", "123.00"),
        # NON_CASH_COST — brak przepływu i nic do zapłaty
        ("100.00", AmountInputType.NET, TaxTreatment.NON_CASH_COST, "0.00", "0.00"),
        ("100.00", AmountInputType.GROSS, TaxTreatment.NON_CASH_COST, "0.00", "0.00"),
    ],
)
def test_cashflow_and_payable(value, input_type, tax_treatment, cashflow, payable):
    amount = Amount.from_input(
        value=Decimal(value),
        input_type=input_type,
        vat_rate=VatRate.VAT_23,
        tax_treatment=tax_treatment,
    )

    assert amount.cashflow == Decimal(cashflow)
    assert amount.payable == Decimal(payable)


def test_cashflow_for_gross_input_equals_net():
    amount = Amount.from_input(
        value=Decimal("246.00"),
        input_type=AmountInputType.GROSS,
        vat_rate=VatRate.VAT_23,
        tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
    )

    assert amount.cashflow == amount.net == Decimal("200.00")
