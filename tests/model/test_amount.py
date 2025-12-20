from decimal import Decimal

from contract_costs.model.amount import Amount, VatRate, TaxTreatment


class TestAmount:

    def test_amount_tax_23(self) -> None:
        amount = Amount(
            value=Decimal("100.00"),
            vat_rate=VatRate.VAT_23,
        )

        assert amount.net == Decimal("100.00")
        assert amount.tax == Decimal("23.00")
        assert amount.gross == Decimal("123.00")
        assert amount.non_tax_cost == Decimal("0.00")

    def test_no_tax(self) -> None:
        amount = Amount(
            value=Decimal("100.00"),
            vat_rate=VatRate.VAT_ZW,
            tax_treatment = TaxTreatment.NON_DEDUCTIBLE,
        )

        assert amount.net is None
        assert amount.tax == Decimal("0.00")
        assert amount.gross == Decimal("100.00")
        assert amount.non_tax_cost == Decimal("100.00")