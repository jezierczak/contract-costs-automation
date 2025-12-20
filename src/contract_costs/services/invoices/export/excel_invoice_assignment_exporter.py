from pathlib import Path

from contract_costs.model.invoice import Invoice
from contract_costs.model.invoice_line import InvoiceLine
from contract_costs.services.invoices.dto.export.assignment_export_bundle import InvoiceAssignmentExportBundle
from contract_costs.services.invoices.export.invoice_assignment_exporter import InvoiceAssignmentExporter


class ExcelInvoiceAssignmentExporter(InvoiceAssignmentExporter):

    def export(
        self,
        bundle: InvoiceAssignmentExportBundle
    ) -> None:
        # openpyxl
        # Sheet 1: INVOICES
        # Sheet 2: INVOICE_LINES
        ...
