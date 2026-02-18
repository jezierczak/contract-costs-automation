from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.financial_records.assigment.apply.apply_company_excel_batch_service import ApplyCompanyExcelBatchService
from contract_costs.services.financial_records.assigment.apply.commands.apply_company_excel_batch_command import \
    ApplyCompanyExcelBatchCommand
from contract_costs.services.financial_records.assigment.apply.commands.apply_invoice_excel_bach_command import \
    ApplyInvoiceExcelBatchCommand
from contract_costs.services.financial_records.assigment.ingest.dto.financial_record_ingest_command import \
    IngestFinancialRecordFromExcelCommand

from contract_costs.services.financial_records.assigment.invoice_sources.excel.invoice_excel_resolver import FinancialRecordExcelBatchResolver
from contract_costs.services.financial_records.assigment.ingest.financial_record_ingest_orchestrator import FinancialRecordIngestOrchestrator
from contract_costs.services.financial_records.assigment.invoice_sources.excel.resolve_financial_record_excel_batch_command import \
    ResolveFinancialRecordExcelBatchCommand
from contract_costs.unit_of_work import UnitOfWork


class ApplyFinancialRecordExcelBatchService(
    ActionHandler[ApplyInvoiceExcelBatchCommand, None]
):
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

    def execute(
            self,
            *,
            action: ApplyInvoiceExcelBatchCommand,
            uow: UnitOfWork,
    ) -> None:
        """
        Contract:
        - faktury bez kompletnych linii NIE są procesowane
        - linie bez invoice_id pozostają kosztami nieewidencjonowanymi
        """

        organization_id = action.organization_id
        actor_user_id = action.actor_user_id
        batch = action.batch

        # =========================
        # 1. Aktualizacja firm
        # =========================

        self._company_apply_service.execute(
            action=ApplyCompanyExcelBatchCommand(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                companies=batch.buyers,
            ),
            uow=uow,
        )

        self._company_apply_service.execute(
            action=ApplyCompanyExcelBatchCommand(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                companies=batch.sellers,
            ),
            uow=uow,
        )

        # =========================
        # 2. Resolver (NIP → UUID)
        # =========================

        ingest_batch = self._excel_resolver.execute(
            action=ResolveFinancialRecordExcelBatchCommand(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                batch=batch
            ),
            uow=uow,
        )

        # =========================
        # 3. Ingest faktur i linii
        # =========================

        self._orchestrator.execute(
            action=IngestFinancialRecordFromExcelCommand(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                batch=ingest_batch,
            ),
            uow=uow,
        )