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
        vat_rate=VatRate.VAT_23,
        tax_treatment=TaxTreatment.NON_DEDUCTIBLE,
    )

    assert amount.net_or_zero == Decimal("0.00")
