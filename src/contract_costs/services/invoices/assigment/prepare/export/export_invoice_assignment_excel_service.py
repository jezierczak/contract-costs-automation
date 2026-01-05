import logging
from pathlib import Path

from contract_costs.services.invoices.assigment.prepare.dto.assignment_export_bundle import InvoiceAssignmentExportBundle
from contract_costs.services.invoices.assigment.prepare.export.invoice_assignment_exporter import InvoiceAssignmentExporter

logger = logging.getLogger(__name__)

class ExportInvoiceAssignmentExcelService:
    def __init__(self,
                 exporter: InvoiceAssignmentExporter,
                 ) -> None:
        self._exporter = exporter

    def execute(
            self,
            bundle: InvoiceAssignmentExportBundle,
            output_path: Path,
    ) -> None:
        self._exporter.export(bundle, output_path)
        logger.info(
            "Generated invoice assignment Excel: invoices=%d, lines=%d, output=%s",
            len(bundle.invoices),
            len(bundle.invoice_lines),
            output_path,
        )