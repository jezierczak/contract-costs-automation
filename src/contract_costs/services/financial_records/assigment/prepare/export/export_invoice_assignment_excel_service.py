import logging
from pathlib import Path
from uuid import UUID

from contract_costs.services.financial_records.assigment.prepare.dto.assignment_export_bundle import FinancialRecordAssignmentExportBundle
from contract_costs.services.financial_records.assigment.prepare.export.invoice_assignment_exporter import InvoiceAssignmentExporter

logger = logging.getLogger(__name__)

class ExportFinancialRecordAssignmentExcelService:
    def __init__(self,
                 exporter: InvoiceAssignmentExporter,
                 ) -> None:
        self._exporter = exporter

    def execute(
            self,
            *,
            organization_id:UUID,
            bundle: FinancialRecordAssignmentExportBundle,
            output_path: Path,
    ) -> None:
        self._exporter.export(
            organization_id=organization_id,
            bundle=bundle,
            output_path=output_path)
        logger.info(
            "Generated invoice assignment Excel: invoices=%d, lines=%d, output=%s",
            len(bundle.records),
            len(bundle.record_lines),
            output_path,
        )