from contract_costs.services.invoices.dto.common import InvoiceExcelBatch
from contract_costs.services.invoices.excel.invoice_excel_resolver import InvoiceExcelBatchResolver
from contract_costs.services.invoices.invoice_line_update_service import InvoiceLineUpdateService
from contract_costs.services.invoices.invoice_update_service import InvoiceUpdateService



class ApplyInvoiceExcelBatchService:
    """
    Zatwierdza dane z excela:
    - aktualizuje / tworzy faktury
    - aktualizuje / tworzy linie faktur
    - FINALIZUJE workflow (status -> PROCESSED)
    """

    def __init__(
        self,
        invoice_service: InvoiceUpdateService,
        invoice_line_service: InvoiceLineUpdateService,
            excel_resolver: InvoiceExcelBatchResolver,
    ) -> None:
        self._invoice_service = invoice_service
        self._invoice_line_service = invoice_line_service
        self._excel_resolver = excel_resolver

    def apply(self, batch: InvoiceExcelBatch) -> None:
        """
        Contract:
        - faktury bez kompletnych linii NIE są procesowane
        - linie bez invoice_id pozostają kosztami nieewidencjonowanymi
        """

        batch = self._excel_resolver.resolve(batch)
        #  Faktury (tworzenie / update + ref_map)
        ref_map = self._invoice_service.apply(batch.invoices)

        # Linie faktur
        finalized_invoice_ids = self._invoice_line_service.apply(batch.lines, ref_map)

        # Finalizacja – status PROCESSED
        self._invoice_service.mark_processed(
            invoice_ids=list(finalized_invoice_ids)
        )