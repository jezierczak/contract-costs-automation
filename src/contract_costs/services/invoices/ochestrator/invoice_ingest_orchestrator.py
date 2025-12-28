from contract_costs.services.invoices.dto.common import  InvoiceIngestBatch

from contract_costs.services.invoices.invoice_line_update_service import InvoiceLineUpdateService
from contract_costs.services.invoices.invoice_update_service import InvoiceUpdateService


class InvoiceIngestOrchestrator:

    def __init__(
        self,
        invoice_service: InvoiceUpdateService,
        invoice_line_service: InvoiceLineUpdateService,
    ) -> None:
        self._invoice_service = invoice_service
        self._invoice_line_service = invoice_line_service

    def ingest_from_pdf(self, batch: InvoiceIngestBatch) -> None:
        """
        PDF → NEW / IN_PROGRESS
        - brak finalizacji
        - brak DELETE / MODIFY
        """

        ref_map = self._invoice_service.apply(batch.invoices)

        self._invoice_line_service.apply(
            batch.lines,
            ref_map,
        )

    def ingest_from_excel(self, batch: InvoiceIngestBatch) -> None:
        """
        Excel → APPLY / MODIFY / DELETE
        - możliwa finalizacja (PROCESSED)
        """



        ref_map = self._invoice_service.apply(batch.invoices)

        finalized_invoice_ids = self._invoice_line_service.apply(
            batch.lines,
            ref_map,
        )

        if finalized_invoice_ids:
            self._invoice_service.mark_processed(
                invoice_ids=list(finalized_invoice_ids)
            )

