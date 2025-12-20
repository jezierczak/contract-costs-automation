from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from contract_costs.model.amount import VatRate, Amount
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository
from contract_costs.repository.inmemory.cost_type_repository import InMemoryCostTypeRepository
from contract_costs.services.invoices.apply_invoice_excel_batch_service import ApplyInvoiceExcelBatchService
from contract_costs.services.invoices.dto.common import InvoiceRef, InvoiceExcelBatch, InvoiceUpdate, InvoiceLineUpdate
from contract_costs.services.invoices.parse_invoice_from_file import (
    ParseInvoiceFromFileService,
)
from contract_costs.services.invoices.invoice_update_service import InvoiceUpdateService
from contract_costs.services.invoices.invoice_line_update_service import InvoiceLineUpdateService
from contract_costs.services.invoices.company_resolve_service import CompanyResolveService

from contract_costs.repository.inmemory.invoice_repository import InMemoryInvoiceRepository
from contract_costs.repository.inmemory.invoice_line_repository import InMemoryInvoiceLineRepository
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository

from contract_costs.model.invoice import InvoiceStatus
from contract_costs.services.invoices.parsers.fake_invoice_parser import FakeInvoiceParser

from contract_costs.services.invoices.generate_assignment_service import (
    GenerateInvoiceAssignmentService,
)
from contract_costs.services.invoices.export.fake_invoice_assignment_exporter import (
    FakeInvoiceAssignmentExporter,
)
from contract_costs.model.invoice import InvoiceStatus

@pytest.fixture(scope="class")
def workflow_context():
    return {
        "invoice_repo": InMemoryInvoiceRepository(),
        "invoice_line_repo": InMemoryInvoiceLineRepository(),
        "company_repo": InMemoryCompanyRepository(),
        "contract_repo": InMemoryContractRepository(),
        "cost_node_repo": InMemoryCostNodeRepository(),
        "cost_type_repo": InMemoryCostTypeRepository(),
    }
class TestWorkflow:

    def test_import_invoice_from_pdf_creates_invoice_and_lines(self,workflow_context):
        # --- services ---
        invoice_repo = workflow_context["invoice_repo"]
        invoice_line_repo = workflow_context["invoice_line_repo"]
        company_repo = workflow_context["company_repo"]

        company_resolver = CompanyResolveService(company_repo)
        invoice_update_service = InvoiceUpdateService(invoice_repo)
        invoice_line_update_service = InvoiceLineUpdateService(invoice_line_repo)

        parser = FakeInvoiceParser()

        import_service = ParseInvoiceFromFileService(
            parser=parser,
            company_resolve_service=company_resolver,
            invoice_update_service=invoice_update_service,
            invoice_line_update_service=invoice_line_update_service,
        )
        #_____________________STEP I parsing from file ___________________________________________________
        # --- execute ---
        import_service.execute(Path("fake.pdf"))

        # --- assertions: invoice ---
        invoices = invoice_repo.list_invoices()
        assert len(invoices) == 1

        invoice = invoices[0]
        assert invoice.invoice_number == "FV/1/2024"
        assert invoice.status == InvoiceStatus.NEW
        assert invoice.buyer_id is not None
        assert invoice.seller_id is not None

        # --- assertions: invoice lines ---
        lines = invoice_line_repo.list_lines()
        assert len(lines) == 1

        line = lines[0]
        assert line.invoice_id == invoice.id
        assert line.description == "Material A"
        assert line.cost_node_id is None
        assert line.cost_type_id is None

        # --- assertions: companies ---
        companies = company_repo.list()
        assert len(companies) == 2

        tax_numbers = {c.tax_number for c in companies}
        assert "1234567890" in tax_numbers
        assert "9999999999" in tax_numbers

#_____________________STEP II sending parsing data to editor for assignment _____________________________________

    def test_generate_invoice_assignment_bundle(self,workflow_context):
        exporter = FakeInvoiceAssignmentExporter()

        service = GenerateInvoiceAssignmentService(
            invoice_repository=workflow_context["invoice_repo"],
            invoice_line_repository=workflow_context["invoice_line_repo"],
            company_repository=workflow_context["company_repo"],
            contract_repository=workflow_context["contract_repo"],
            cost_node_repository=workflow_context["cost_node_repo"],
            cost_type_repository=workflow_context["cost_type_repo"],
            exporter=exporter,
        )
        # --- execute ---
        service.execute()

        # --- assertions: bundle ---
        bundle = exporter.bundle
        assert bundle is not None

        assert len(bundle.invoices) == 1

        inv = bundle.invoices[0]
        assert inv.invoice_number == "FV/1/2024"
        assert inv.status == InvoiceStatus.IN_PROGRESS

        assert len(bundle.invoice_lines) == 1

        line = bundle.invoice_lines[0]
        assert line.description == "Material A"
        assert line.net == Decimal("200")
        assert line.vat_rate == VatRate.VAT_23
        assert line.contract_id is None
        assert line.cost_node_id is None

        assert len(bundle.companies) == 2
        tax_numbers = {c.tax_number for c in bundle.companies}
        assert "1234567890" in tax_numbers
        assert "9999999999" in tax_numbers

        assert bundle.contracts == []
        assert bundle.cost_nodes == []
        assert bundle.cost_types == []

#_____________________STEP III getting back assigment data _____________________________________

    def test_apply_invoice_excel_batch(self,workflow_context):
        invoice_repo = workflow_context["invoice_repo"]
        invoice_line_repo = workflow_context["invoice_line_repo"]

        invoices = invoice_repo.list_invoices()
        assert len(invoices) == 1
        invoice = invoices[0]

        lines = invoice_line_repo.list_lines()
        assert len(lines) == 1
        line = lines[0]

        # --- GIVEN: batch from "excel" ---
        ref = InvoiceRef(invoice_id=invoice.id, external_ref="PDF-001")

        batch = InvoiceExcelBatch(
            invoices=[
                InvoiceUpdate(
                    ref=ref,
                    invoice_number="FV/1/2024",
                    invoice_date=invoice.invoice_date,
                    selling_date=invoice.selling_date,
                    buyer_id=invoice.buyer_id,
                    seller_id=invoice.seller_id,
                    payment_method=invoice.payment_method,
                    payment_status=invoice.payment_status,
                    due_date=invoice.due_date,
                    status=InvoiceStatus.PROCESSED,
                )
            ],
            lines=[
                # update existing line
                InvoiceLineUpdate(
                    invoice_line_id=line.id,
                    invoice_ref=ref,
                    description="Material A (updated)",
                    quantity=Decimal("3"),
                    unit=UnitOfMeasure.PIECE,
                    amount=Amount(Decimal("300"), VatRate.VAT_23),
                    contract_id=uuid4(),
                    cost_node_id=uuid4(),
                    cost_type_id=uuid4(),
                ),
                # new line (manual cost)
                InvoiceLineUpdate(
                    invoice_line_id=None,
                    invoice_ref=ref,
                    description="Extra work",
                    quantity=Decimal("1"),
                    unit=UnitOfMeasure.SERVICE,
                    amount=Amount(Decimal("500"), VatRate.VAT_8),
                    contract_id=uuid4(),
                    cost_node_id=uuid4(),
                    cost_type_id=uuid4(),
                ),
            ],
        )

        # --- WHEN ---
        service = ApplyInvoiceExcelBatchService(
            invoice_service=InvoiceUpdateService(invoice_repo),
            invoice_line_service=InvoiceLineUpdateService(invoice_line_repo),
        )

        service.apply(batch)

        # --- THEN: invoice ---
        updated_invoice = invoice_repo.get(invoice.id)
        assert updated_invoice is not None
        assert updated_invoice.status == InvoiceStatus.PROCESSED

        # --- THEN: invoice lines ---
        updated_lines = invoice_line_repo.list_lines()
        assert len(updated_lines) == 2

        descriptions = {l.description for l in updated_lines}
        assert "Material A (updated)" in descriptions
        assert "Extra work" in descriptions


