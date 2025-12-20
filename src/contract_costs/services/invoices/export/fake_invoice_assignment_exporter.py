from contract_costs.services.invoices.export.invoice_assignment_exporter import (
    InvoiceAssignmentExporter,
)
from contract_costs.services.invoices.dto.export.assignment_export_bundle import (
    InvoiceAssignmentExportBundle,
)

class FakeInvoiceAssignmentExporter(InvoiceAssignmentExporter):
    def __init__(self) -> None:
        self.bundle: InvoiceAssignmentExportBundle | None = None

    def export(self, bundle: InvoiceAssignmentExportBundle) -> None:
        self.bundle = bundle
