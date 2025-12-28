from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from contract_costs.model.amount import VatRate, Amount
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.repository.inmemory.cost_node_repository import InMemoryCostNodeRepository
from contract_costs.repository.inmemory.cost_type_repository import InMemoryCostTypeRepository
from contract_costs.services.catalogues.invoice_file_organizer import InvoiceFileOrganizer
from contract_costs.services.invoices.apply_invoice_excel_batch_service import ApplyInvoiceExcelBatchService
from contract_costs.services.invoices.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.dto.common import InvoiceExcelBatch, InvoiceUpdate, InvoiceLineUpdate
from contract_costs.services.invoices.normalization.invoice_parser_normalizer import InvoiceParseNormalizer
from contract_costs.services.invoices.ochestrator.invoice_ingest_orchestrator import InvoiceIngestOrchestrator
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
        contract_repo = workflow_context["contract_repo"]
        cost_node_repo = workflow_context["cost_node_repo"]
        cost_type_repo = workflow_context["cost_type_repo"]



