import logging
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler

from contract_costs.services.catalogues.record_file_workworkflow_service import RecordFileWorkflowService
from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_reason import \
    FinancialRecordCompletionReason
from contract_costs.services.financial_records.assigment.ingest.dto.financial_record_ingest_command import \
    BaseFinancialRecordIngestCommand, IngestFinancialRecordFromDocumentCommand, IngestFinancialRecordFromExcelCommand
from contract_costs.services.financial_records.assigment.ingest.excel_financial_record_ingest_service import ExcelFinancialRecordIngestService
from contract_costs.services.financial_records.assigment.ingest.completion_validator.invoice_completion_validator import RecordCompletionValidator
from contract_costs.services.financial_records.assigment.ingest.pdf_financial_record_ingest_service import PdfFinancialRecordIngestService
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import  RecordIngestBatch

from contract_costs.services.financial_records.assigment.ingest.financial_record_line_update_service import FinancialRecordLineUpdateService
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

class FinancialRecordIngestOrchestrator(ActionHandler[BaseFinancialRecordIngestCommand, UUID | None]):

    def __init__(
            self,
            record_ingest_service_document: PdfFinancialRecordIngestService,
            record_ingest_service_excel: ExcelFinancialRecordIngestService,
            record_line_service: FinancialRecordLineUpdateService,
            file_workflow: RecordFileWorkflowService,
            record_completion_validator: RecordCompletionValidator,
    ) -> None:
        self._document_ingest = record_ingest_service_document
        self._excel_ingest = record_ingest_service_excel
        self._record_line_service = record_line_service
        self._file_workflow = file_workflow
        self._completion_validator = record_completion_validator

    def execute(
            self,
            *,
            action: BaseFinancialRecordIngestCommand,
            uow: UnitOfWork,
    ):
        if isinstance(action, IngestFinancialRecordFromDocumentCommand):
            return self._ingest_from_document(
                uow=uow,
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                batch=action.batch,
            )

        if isinstance(action, IngestFinancialRecordFromExcelCommand):
            return self._ingest_from_excel(
                uow=uow,
                organization_id=action.organization_id,
                actor_user_id=action.actor_user_id,
                batch=action.batch,
            )

        raise RuntimeError("Unsupported ingest command type")

    def _ingest_from_document(
            self,
            *,
            uow:UnitOfWork,
            organization_id: UUID,
            actor_user_id: UUID,
            batch: RecordIngestBatch,
    ) -> UUID:
        """
        PDF → NEW / IN_PROGRESS
        - brak finalizacji
        - brak DELETE / MODIFY
        """

        ref_map = self._document_ingest.apply(
            uow=uow,
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            updates=batch.financial_records)
        self._record_line_service.apply(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            lines=batch.lines,
            ref_map=ref_map,
            uow=uow
        )

        record_ids = [
            ref.record_id
            for ref in ref_map.values()
            if ref.record_id
        ]

        if len(record_ids) != 1:
            raise RuntimeError("Document ingest expected exactly one record")

        return record_ids[0]

    def _ingest_from_excel(
            self,
            *,
            uow: UnitOfWork,
            organization_id: UUID,
            actor_user_id: UUID,
            batch: RecordIngestBatch,
    ) -> None:
        """
          Excel → APPLY / MODIFY / DELETE
          - możliwa finalizacja (PROCESSED)
          """

        # =========================
        # 1. Faktury (create / update / delete)
        # =========================

        ref_map = self._excel_ingest.apply(
            uow=uow,
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            updates=batch.financial_records
        )

        # =========================
        # 2. Linie faktur
        # =========================

        assignment_facts = self._record_line_service.apply(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            lines=batch.lines,
            ref_map=ref_map,
            uow=uow
        )

        # =========================
        # 3. Walidacja kompletności
        # =========================

        to_finalize: list[UUID] = []

        for facts in assignment_facts.values():
            if facts.record_id is None:
                continue

            reasons = self._completion_validator.status(facts)

            for reason in reasons:
                logger.info(
                    "[RECORD_COMPLETION] org=%s record_id=%s reason=%s",
                    organization_id,
                    facts.record_id,
                    reason.value,
                )

            if FinancialRecordCompletionReason.OK in reasons:
                to_finalize.append(facts.record_id)

        # =========================
        # 4. Finalizacja (PROCESSED)
        # =========================

        if to_finalize:
            self._excel_ingest.mark_processed(
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                record_ids=to_finalize,
                record_repo=uow.financial_records
            )

        # =========================
        # 5. Sync plików
        # =========================

        for ref in ref_map.values():
            if not ref.record_id:
                continue

            record = uow.financial_records.get(
                organization_id=organization_id,
                record_id=ref.record_id,
            )
            if record is None:
                raise RuntimeError(
                    f"Invoice not found (org={organization_id}, id={ref.record_id})"
                )

            self._file_workflow.sync(
                organization_id=organization_id,
                record=record,
                uow=uow,
            )
