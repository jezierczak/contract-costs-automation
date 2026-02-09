from pathlib import Path
from uuid import UUID

from contract_costs.services.financial_records.assigment.prepare.export.invoice_assignment_exporter import (
    InvoiceAssignmentExporter,
)
from contract_costs.services.financial_records.assigment.prepare.dto.assignment_export_bundle import (
    FinancialRecordAssignmentExportBundle,
)

class FakeInvoiceAssignmentExporter(InvoiceAssignmentExporter):
    def __init__(self) -> None:
        self.bundle: FinancialRecordAssignmentExportBundle | None = None

    def export(self,
               organization_id: UUID,
               bundle: FinancialRecordAssignmentExportBundle,
               output_path: Path) -> None:
        self.bundle = bundle
