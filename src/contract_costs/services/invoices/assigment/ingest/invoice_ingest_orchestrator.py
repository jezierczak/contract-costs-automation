from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.catalogues.invoice_file_workflow_service import InvoiceFileWorkflowService
from contract_costs.services.invoices.assigment.ingest.excel_invoice_ingest_service import ExcelInvoiceIngestService
from contract_costs.services.invoices.assigment.ingest.pdf_invoice_ingest_service import PdfInvoiceIngestService
from contract_costs.services.invoices.assigment.invoice_sources.dto.common import  InvoiceIngestBatch

from contract_costs.services.invoices.assigment.ingest.invoice_line_update_service import InvoiceLineUpdateService


class InvoiceIngestOrchestrator:

    def __init__(
            self,
            invoice_ingest_service_pdf: PdfInvoiceIngestService,
            invoice_ingest_service_excel: ExcelInvoiceIngestService,
            invoice_line_service: InvoiceLineUpdateService,
            invoice_repository: InvoiceRepository,
            file_workflow: InvoiceFileWorkflowService,
    ) -> None:
        self._pdf_ingest = invoice_ingest_service_pdf
        self._excel_ingest = invoice_ingest_service_excel
        self._invoice_line_service = invoice_line_service
        self._invoice_repository = invoice_repository
        self._file_workflow = file_workflow

    def ingest_from_pdf(self, batch: InvoiceIngestBatch) -> None:
        """
        PDF → NEW / IN_PROGRESS
        - brak finalizacji
        - brak DELETE / MODIFY
        """

        ref_map = self._pdf_ingest.apply(batch.invoices)
        self._invoice_line_service.apply(
            batch.lines,
            ref_map,
        )

        for ref in ref_map.values():
            if ref.invoice_id:
                invoice = self._invoice_repository.get(ref.invoice_id)
                if invoice is None:
                    raise RuntimeError(
                        f"Invoice not found for id {ref.invoice_id}"
                    )
                self._file_workflow.sync(invoice)

    def ingest_from_excel(self, batch: InvoiceIngestBatch) -> None:
        """
        Excel → APPLY / MODIFY / DELETE
        - możliwa finalizacja (PROCESSED)
        """



        ref_map = self._excel_ingest.apply(batch.invoices)

        finalized_invoice_ids = self._invoice_line_service.apply(
            batch.lines,
            ref_map,
        )

        if finalized_invoice_ids:
            self._excel_ingest.mark_processed(
                invoice_ids=list(finalized_invoice_ids)
            )

        for ref in ref_map.values():
            if ref.invoice_id:
                invoice = self._invoice_repository.get(ref.invoice_id)
                if invoice is None:
                    raise RuntimeError(
                        f"Invoice not found for id {ref.invoice_id}"
                    )
                self._file_workflow.sync(invoice)
