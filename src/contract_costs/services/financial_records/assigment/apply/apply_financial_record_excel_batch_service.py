from contract_costs.services.financial_records.assigment.apply.apply_company_excel_batch_service import ApplyCompanyExcelBatchService
from contract_costs.services.financial_records.assigment.apply.commands.apply_invoice_excel_bach_command import \
    ApplyInvoiceExcelBatchCommand

from contract_costs.services.financial_records.assigment.invoice_sources.excel.invoice_excel_resolver import FinancialRecordExcelBatchResolver
from contract_costs.services.financial_records.assigment.ingest.financial_record_ingest_orchestrator import FinancialRecordIngestOrchestrator


class ApplyFinancialRecordExcelBatchService:
    """
    Zatwierdza dane z excela:
    - aktualizuje / tworzy faktury
    - aktualizuje / tworzy linie faktur
    - FINALIZUJE workflow (status -> PROCESSED)
    """

    def __init__(
        self,
        excel_resolver: FinancialRecordExcelBatchResolver,
        company_apply_service: ApplyCompanyExcelBatchService,
        orchestrator: FinancialRecordIngestOrchestrator
    ) -> None:
        self._excel_resolver = excel_resolver
        self._company_apply_service = company_apply_service
        self._orchestrator = orchestrator

    def execute(self, cmd: ApplyInvoiceExcelBatchCommand) -> None:
        """
        Contract:
        - faktury bez kompletnych linii NIE są procesowane
        - linie bez invoice_id pozostają kosztami nieewidencjonowanymi
        """

        organization_id = cmd.organization_id
        actor_user_id = cmd.actor_user_id
        batch = cmd.batch

        # =========================
        # 1. Aktualizacja firm
        # =========================

        self._company_apply_service.apply(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            companies=batch.buyers,
        )

        self._company_apply_service.apply(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            companies=batch.sellers,
        )

        # =========================
        # 2. Resolver (NIP → UUID)
        # =========================

        ingest_batch = self._excel_resolver.resolve(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            batch=batch,
        )

        # =========================
        # 3. Ingest faktur i linii
        # =========================

        self._orchestrator.ingest_from_excel(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            batch=ingest_batch,
        )
