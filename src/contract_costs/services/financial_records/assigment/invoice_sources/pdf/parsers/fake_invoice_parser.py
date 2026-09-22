
from decimal import Decimal
from datetime import date

from contract_costs.model.document import DocumentType
from contract_costs.model.financial_record import PaymentMethod, PaymentStatus, FinancialRecordStatus
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.document_parser import DocumentParser
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import (
    DocumentParseResult,
    FinancialRecordUpdate,
    FinancialRecordLineUpdate,
    CompanyInput,
)
from contract_costs.model.amount import AmountInputType, VatRate, Amount
from contract_costs.model.unit_of_measure import UnitOfMeasure

class FakeDocumentParser(DocumentParser):

    def parse(self, file_path):
        # invoice_ref: InvoiceRef = InvoiceRef(invoice_id=None, external_ref="PDF-001")

        return DocumentParseResult(
            document_type=DocumentType.INVOICE,
            record=FinancialRecordUpdate(

                command=InvoiceCommand.APPLY,
                record_id=None,
                reference="FV/1/2024",
                old_reference=None,
                invoice_date=date(2024, 1, 10),
                selling_date=date(2024, 1, 10),
                buyer_tax_number=None,
                seller_tax_number=None,
                payment_method=PaymentMethod.BANK_TRANSFER,
                payment_status=PaymentStatus.UNPAID,
                status=FinancialRecordStatus.NEW_COST,
                due_date=date(2024, 1, 20),
                paid_date=None,
                tags=None
            ),
            lines=[
                FinancialRecordLineUpdate(
                    record_line_id=None,
                    record_reference="PDF-001",
                    item_name="Item name",
                    description="Material A",
                    quantity=Decimal("2"),
                    unit=UnitOfMeasure.PIECE,
                    amount=Amount(
                        value=Decimal("200"),
                        input_type=AmountInputType.NET,
                        vat_rate=VatRate.VAT_23,
                    ),

                    contract_reference=None,
                    contract_node_reference=None,
                    value_type_reference=None,
                    agreement_reference=None,
                    agreement_node_reference=None,
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

