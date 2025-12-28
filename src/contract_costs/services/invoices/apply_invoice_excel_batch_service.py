from uuid import UUID

from contract_costs.services.invoices.apply_company_excel_batch_service import ApplyCompanyExcelBatchService
from contract_costs.services.invoices.dto.common import InvoiceExcelBatch
from contract_costs.services.invoices.excel.invoice_excel_resolver import InvoiceExcelBatchResolver
from contract_costs.services.invoices.invoice_line_update_service import InvoiceLineUpdateService
from contract_costs.services.invoices.invoice_update_service import InvoiceUpdateService
from contract_costs.services.invoices.ochestrator.invoice_ingest_orchestrator import InvoiceIngestOrchestrator


class ApplyInvoiceExcelBatchService:
    """
    Zatwierdza dane z excela:
    - aktualizuje / tworzy faktury
    - aktualizuje / tworzy linie faktur
    - FINALIZUJE workflow (status -> PROCESSED)
    """

    def __init__(
        self,
        excel_resolver: InvoiceExcelBatchResolver,
        company_apply_service: ApplyCompanyExcelBatchService,
        orchestrator: InvoiceIngestOrchestrator
    ) -> None:
        self._excel_resolver = excel_resolver
        self._company_apply_service = company_apply_service
        self._orchestrator = orchestrator

    def apply(self, batch: InvoiceExcelBatch) -> None:
        """
        Contract:
        - faktury bez kompletnych linii NIE są procesowane
        - linie bez invoice_id pozostają kosztami nieewidencjonowanymi
        """

        #  Aktualizacja firm (NOWE)

        # Resolver (NIP → UUID)

        self._company_apply_service.apply(batch.buyers)
        self._company_apply_service.apply(batch.sellers)

        batch = self._excel_resolver.resolve(batch)

        self._orchestrator.ingest_from_excel(
         batch=batch
        )

