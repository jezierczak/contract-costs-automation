from decimal import Decimal
from uuid import uuid4
from datetime import date, datetime

from contract_costs.model.invoice import Invoice, InvoiceStatus, PaymentMethod, PaymentStatus
from contract_costs.model.amount import Amount, VatRate, TaxTreatment
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository
from contract_costs.services.invoices.invoice_total_service import InvoiceTotalsService


class TestInvoiceTotalService:


    def test_invoice_totals(self, contract_owner, contract_company) -> None:
        invoice_id = uuid4()

        lines = [
            InvoiceLine(
                id=uuid4(),
                invoice_id=invoice_id,
                quantity=Decimal("2"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(
                    value=Decimal("100"),
                    vat_rate=VatRate.VAT_23,
                ),
                contract_id=uuid4(),
                cost_node_id=uuid4(),
                cost_type_id=uuid4(),
                description="Material",
            ),
            InvoiceLine(
                id=uuid4(),
                invoice_id=invoice_id,
                quantity=Decimal("1"),
                unit=UnitOfMeasure.SERVICE,
                amount=Amount(
                    value=Decimal("200"),
                    vat_rate=VatRate.VAT_0,
                    tax_treatment=TaxTreatment.NON_DEDUCTIBLE,
                ),
                contract_id=uuid4(),
                cost_node_id=uuid4(),
                cost_type_id=uuid4(),
                description="Non tax cost",
            ),
        ]

        invoice = Invoice(
            id=invoice_id,
            invoice_number="FV/1",
            invoice_date=date.today(),
            selling_date=date.today(),
            buyer_id= contract_owner.id,
            seller_id=contract_company.id,
            payment_method=PaymentMethod.CASH,
            due_date=date.today(),
            payment_status=PaymentStatus.UNPAID,
            status=InvoiceStatus.NEW,
            timestamp=datetime.now(),
        )

        invoice_lines_repo = InMemoryInvoiceLineRepository()
        for invoice_line in lines:
            invoice_lines_repo.add(invoice_line)

        invoice_totals = InvoiceTotalsService(invoice_lines_repo).calculate(invoice_id=invoice_id)

        assert invoice_totals.net == Decimal("100.00")
        assert invoice_totals.tax == Decimal("23.00")
        assert invoice_totals.gross == Decimal("323.00")
