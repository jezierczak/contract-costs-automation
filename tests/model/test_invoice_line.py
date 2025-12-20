from decimal import Decimal
from uuid import uuid4

from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.unit_of_measure import UnitOfMeasure


class TestInvoiceLine:

    def test_invoice_line_amount(self,) -> None:
        line = InvoiceLine(
            id=uuid4(),
            invoice_id=uuid4(),
            quantity= Decimal("2"),
            unit=UnitOfMeasure.PIECE,
            amount=Amount(
                value=Decimal("100"),
                vat_rate=VatRate.VAT_23,
            ),
            contract_id=uuid4(),
            cost_node_id=uuid4(),
            cost_type_id=uuid4(),
            description="Test line"
        )

        assert line.amount.net == Decimal("100")
        assert line.amount.tax == Decimal("23")
        assert line.amount.gross == Decimal("123")

    def test_invoice_line_quantity_and_unit(self) -> None:
        line = InvoiceLine(
            id=uuid4(),
            invoice_id=uuid4(),
            quantity=Decimal("3"),
            unit=UnitOfMeasure.HOUR,
            amount=Amount(
                value=Decimal("50"),
                vat_rate=VatRate.VAT_8,
            ),
            contract_id=uuid4(),
            cost_node_id=uuid4(),
            cost_type_id=uuid4(),
            description="Work",
        )

        assert line.quantity == 3
        assert line.unit == UnitOfMeasure.HOUR