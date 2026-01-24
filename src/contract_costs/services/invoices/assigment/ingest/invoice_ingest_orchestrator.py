import logging
from uuid import UUID

from contract_costs.repository.invoice_repository import InvoiceRepository
from contract_costs.services.catalogues.invoice_file_workflow_service import InvoiceFileWorkflowService
from contract_costs.services.invoices.assigment.ingest.completion_validator.invoice_completion_reason import \
    InvoiceCompletionReason
from contract_costs.services.invoices.assigment.ingest.excel_invoice_ingest_service import ExcelInvoiceIngestService
from contract_costs.services.invoices.assigment.ingest.completion_validator.invoice_completion_validator import InvoiceCompletionValidator
from contract_costs.services.invoices.assigment.ingest.pdf_invoice_ingest_service import PdfInvoiceIngestService
from contract_costs.services.invoices.assigment.invoice_sources.dto.common import  InvoiceIngestBatch

from contract_costs.services.invoices.assigment.ingest.invoice_line_update_service import InvoiceLineUpdateService


logger = logging.getLogger(__name__)

class InvoiceIngestOrchestrator:

    def __init__(
            self,
            invoice_ingest_service_pdf: PdfInvoiceIngestService,
            invoice_ingest_service_excel: ExcelInvoiceIngestService,
            invoice_line_service: InvoiceLineUpdateService,
            invoice_repository: InvoiceRepository,
            file_workflow: InvoiceFileWorkflowService,
            invoice_completion_validator: InvoiceCompletionValidator,
    ) -> None:
        self._pdf_ingest = invoice_ingest_service_pdf
        self._excel_ingest = invoice_ingest_service_excel
        self._invoice_line_service = invoice_line_service
        self._invoice_repository = invoice_repository
        self._file_workflow = file_workflow
        self._completion_validator = invoice_completion_validator

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

        assignment_facts = self._invoice_line_service.apply(
            batch.lines,
            ref_map,
        )

        to_finalize: list[UUID] = []

        for facts in assignment_facts.values():
            if facts.invoice_id is None:
                continue

            reasons = self._completion_validator.status(facts)

            for reason in reasons:
                logger.info(
                    "[INVOICE_COMPLETION] invoice_id=%s reason=%s",
                    facts.invoice_id,
                    reason.value,
                )

            if InvoiceCompletionReason.OK in reasons:
                to_finalize.append(facts.invoice_id)

        if to_finalize:
            self._excel_ingest.mark_processed(to_finalize)



        for ref in ref_map.values():
            if ref.invoice_id:
                invoice = self._invoice_repository.get(ref.invoice_id)
                if invoice is None:
                    raise RuntimeError(
                        f"Invoice not found for id {ref.invoice_id}"
                    )
                self._file_workflow.sync(invoice)
