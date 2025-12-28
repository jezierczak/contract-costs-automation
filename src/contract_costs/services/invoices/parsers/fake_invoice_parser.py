
from decimal import Decimal
from datetime import date


from contract_costs.model.invoice import PaymentMethod, PaymentStatus, InvoiceStatus
from contract_costs.services.invoices.commands.invoice_command import InvoiceCommand

from contract_costs.services.invoices.parsers.invoice_parser import InvoiceParser
from contract_costs.services.invoices.dto.parse import (
    InvoiceParseResult,
    InvoiceUpdate,
    InvoiceLineUpdate,
    CompanyInput,
)
from contract_costs.model.amount import VatRate, TaxTreatment, Amount
from contract_costs.model.unit_of_measure import UnitOfMeasure

class FakeInvoiceParser(InvoiceParser):

    def parse(self, file_path):
        # invoice_ref: InvoiceRef = InvoiceRef(invoice_id=None, external_ref="PDF-001")

        return InvoiceParseResult(
            invoice=InvoiceUpdate(

                command=InvoiceCommand.APPLY,
                invoice_number="FV/1/2024",
                old_invoice_number=None,
                invoice_date=date(2024, 1, 10),
                selling_date=date(2024, 1, 10),
                buyer_tax_number=None,
                seller_tax_number=None,
                payment_method=PaymentMethod.BANK_TRANSFER,
                payment_status=PaymentStatus.UNPAID,
                status=InvoiceStatus.NEW,
                due_date=date(2024, 1, 20),

            ),
            lines=[
                InvoiceLineUpdate(
                    invoice_line_id=None,
                    invoice_number="PDF-001",
                    item_name="Item name",
                    description="Material A",
                    quantity=Decimal("2"),
                    unit=UnitOfMeasure.PIECE,
                    amount=Amount(Decimal("200"),VatRate.VAT_23),

                    contract_id=None,
                    cost_node_id=None,
                    cost_type_id=None,
                )
            ],
            buyer=CompanyInput(
                name="Client Sp. z o.o.",
                street="ulica",
                city="City",
                state="malopolska",
                zip_code="55-999",
                country="PL",
                phone_number="123456789",
                email="email@email.com",
                bank_account = "10203040203020304040404030",
                tax_number="1234567890",
                role= "Own",
            ),
            seller=CompanyInput(
                name="My Company",
                street="ulica2",
                city="City2",
                state="malopolska2",
                zip_code="52-999",
                country="PL",
                phone_number="1232456789",
                email="em2ail@email.com",
                bank_account="10203040203020304040404030",
                tax_number="9999999999",
                role="Client",
            )
        )

