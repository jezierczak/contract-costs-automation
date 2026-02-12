import logging
from dataclasses import replace
from uuid import UUID

from contract_costs.model.company import CompanyType
from contract_costs.model.document import Document, DocumentType
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.repository.financial_record_repository import FinancialRecordRepository

from contract_costs.services.catalogues.record_file_organizer import RecordFileOrganizer
from contract_costs.services.catalogues.record_file_workworkflow_service import RecordFileWorkflowService
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    ResolvedFinancialRecordUpdate,
    RecordIngestBatch,
)
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import (
    DocumentParseNormalizer,
)
from contract_costs.services.financial_records.assigment.ingest.financial_record_ingest_orchestrator import (
    FinancialRecordIngestOrchestrator,
)
from contract_costs.repository.document_repository import DocumentRepository

import contract_costs.config as cfg
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import \
    DocumentParseResult

logger = logging.getLogger(__name__)


class CreateRecordFromDocumentService:
    """
    Rebuild financial record from already parsed Document.

    Flow:
    DOCUMENT (with payload)
        → normalize
        → company evaluate
        → build ingest batch
        → ingest
        → move file to RAW
        → attach document
    """

    def __init__(
        self,
        company_evaluate: CompanyEvaluateOrchestrator,
        normalizer: DocumentParseNormalizer,
        ingest_orchestrator: FinancialRecordIngestOrchestrator,
        record_file_organizer: RecordFileOrganizer,
        document_repository: DocumentRepository,
        record_repository: FinancialRecordRepository,
        file_workflow: RecordFileWorkflowService
    ) -> None:
        self._company_evaluate = company_evaluate
        self._normalizer = normalizer
        self._ingest = ingest_orchestrator
        self._file_organizer = record_file_organizer
        self._documents = document_repository
        self._record_repository = record_repository
        self._file_workflow = file_workflow

    # ============================================================
    # PUBLIC API
    # ============================================================

    def execute(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        document: Document,
        override_reference: str | None = None,
        override_seller_nip: str | None = None,
        override_document_type: DocumentType | None = None,
    ) -> UUID:
        """
        Creates new FinancialRecord from existing Document payload.

        Returns:
            newly created record_id
        """

        if not document.parsed_payload:
            raise RuntimeError("Document has no parsed payload")

        if document.financial_record_id is not None:
            raise RuntimeError("Document already attached to record")

        logger.info(
            "Creating record from document %s",
            document.id,
        )

        # ============================================================
        # 1️⃣ REBUILD PARSE RESULT FROM PAYLOAD
        # ============================================================

        parse_result: DocumentParseResult = self._normalizer.normalize_payload(
            document.parsed_payload
        )

        # ============================================================
        # 2️⃣ APPLY USER OVERRIDES
        # ============================================================

        if override_reference:
            parse_result = replace(
                parse_result,
                record=replace(
                    parse_result.record,
                    reference=override_reference,
                ),
            )

        if override_seller_nip:
            parse_result = replace(
                parse_result,
                seller=replace(
                    parse_result.seller,
                    tax_number=override_seller_nip,
                ),
            )

        if override_document_type:
            parse_result = replace(
                parse_result,
                document_type=override_document_type,
            )

        # ============================================================
        # 3️⃣ COMPANY RESOLUTION
        # ============================================================

        buyer = self._company_evaluate.evaluate(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            input_=parse_result.buyer,
        )

        seller = self._company_evaluate.evaluate(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            input_=parse_result.seller,
        )

        # ============================================================
        # 4️⃣ STATUS RESOLUTION
        # ============================================================

        if buyer.role == CompanyType.OWN and buyer.is_active:
            status = FinancialRecordStatus.NEW_COST

        elif seller.role == CompanyType.OWN and seller.is_active:
            status = FinancialRecordStatus.NEW_REVENUE

        else:
            status = FinancialRecordStatus.DRAFT

        # # ============================================================
        # # 5️⃣ MOVE FILE → RAW
        # # ============================================================
        #
        # org_root = cfg.WORK_DIR / str(organization_id)
        #
        # raw_path = self._file_organizer.move_to_raw(
        #     root=org_root,
        #     file_path=org_root / document.file_path,
        # )

        # ============================================================
        # 6️⃣ BUILD RECORD UPDATE
        # ============================================================

        record_update = [
            ResolvedFinancialRecordUpdate(
                command=parse_result.record.command,
                reference=parse_result.record.reference,
                record_id=None,
                old_record_reference=parse_result.record.old_reference,
                invoice_date=parse_result.record.invoice_date,
                selling_date=parse_result.record.selling_date,
                buyer=buyer,
                seller=seller,
                payment_method=parse_result.record.payment_method,
                due_date=parse_result.record.due_date,
                paid_date=parse_result.record.paid_date,
                payment_status=parse_result.record.payment_status,
                status=status,
                # scan_filename=raw_path.as_posix(),
                tags=None,
            )
        ]

        line_updates = [
            replace(line, record_reference=parse_result.record.reference)
            for line in parse_result.lines
        ]

        batch = RecordIngestBatch(
            financial_records=record_update,
            lines=line_updates,
        )

        # ============================================================
        # 7️⃣ INGEST
        # ============================================================

        new_record_id = self._ingest.ingest_from_document(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            batch=batch,
        )

        # ============================================================
        # 8️⃣ ATTACH DOCUMENT
        # ============================================================

        self._documents.attach_to_record(
            organization_id=organization_id,
            document_id=document.id,
            record_id=new_record_id,
        )

        record = self._record_repository.get(
            organization_id=organization_id,
            record_id=new_record_id,
        )
        if record:
            self._file_workflow.sync(
                organization_id=organization_id,
                record=record,
            )

        # # zapisz zmiany file_path dokumentów
        # for doc in record.documents:
        #     self._documents.update(doc)

        logger.info(
            "Record created from document %s → record %s",
            document.id,
            new_record_id,
        )

        return new_record_id
