from datetime import datetime
from dataclasses import replace
from typing import Callable
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.company import CompanyType
from contract_costs.model.document import Document, DocumentType
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.repository.financial_record_repository import FinancialRecordRepository
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.catalogues.record_file_workworkflow_service import RecordFileWorkflowService
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator, EvaluateMode
from contract_costs.services.documents.apply.dto.apply_document_command import ApplyDocumentCommand, DocumentApplyAction
from contract_costs.services.financial_records.assigment.invoice_sources.document.create_record_from_document_service import \
    CreateRecordFromDocumentService
import contract_costs.config as cfg

class ApplyDocumentService:

    def __init__(
        self,
        document_repo: DocumentRepository,
        record_repo: FinancialRecordRepository,
        company_evaluator: CompanyEvaluateOrchestrator,
        create_record_service: CreateRecordFromDocumentService,
        file_organizer: DocumentFileOrganizer,
        file_service: RecordFileWorkflowService,
        clock: Callable[[], datetime] = utc_now,
        id_generator: Callable[[], UUID] = new_uuid,
    ) -> None:
        self._documents = document_repo
        self._records = record_repo
        self._company_eval = company_evaluator
        self._create_record_service = create_record_service
        self._files = file_organizer
        self._clock = clock
        self._id_generator=id_generator
        self._file_workflow_service = file_service

    # ============================================================
    # ENTRY POINT
    # ============================================================

    def execute(self, cmd: ApplyDocumentCommand) -> None:

        document = self._documents.get(
            organization_id=cmd.organization_id,
            document_id=cmd.document_id,
        )



        if not document:
            raise RuntimeError("Document not found")

        if document.financial_record_id:
            raise RuntimeError("Document already assigned")

        if not document.parsed_payload:
            raise RuntimeError("Document not parsed")

        # --------------------------------------------------------
        # 1️⃣ APPLY OVERRIDES
        # --------------------------------------------------------

        document = self._apply_overrides(document, cmd)

        self._documents.update(document)

        # --------------------------------------------------------
        # 2️⃣ SWITCH ACTION
        # --------------------------------------------------------

        match cmd.action:

            case DocumentApplyAction.CREATE_NEW:
                self._create_new(cmd, document)

            case DocumentApplyAction.ADD_TO_EXISTING:
                self._attach_existing(cmd, document)

            case DocumentApplyAction.SKIP:
                self._skip(document)

            case DocumentApplyAction.DELETE:
                self._delete(document)

            case _:
                raise RuntimeError("Unknown action")

    @staticmethod
    def _apply_overrides(
        document: Document,
        cmd: ApplyDocumentCommand,
    ) -> Document:
        updated = document
        if cmd.override_document_type:
            updated = updated.with_document_type(
                DocumentType(cmd.override_document_type)
            )
        if cmd.override_document_number:
            updated = updated.with_document_number(
                cmd.override_document_number
            )
        if cmd.override_seller_nip:
            updated = updated.with_seller_nip(
                cmd.override_seller_nip
            )
        return updated


    def _create_new(
        self,
        cmd: ApplyDocumentCommand,
        document: Document,
    ) -> None:

        record_id = self._create_record_service.execute(
            organization_id=cmd.organization_id,
            actor_user_id=cmd.actor_user_id,
            document=document,
            override_reference=cmd.override_document_number,
            override_seller_nip=cmd.override_seller_nip,
            override_document_type=DocumentType(cmd.override_document_type),
        )

    def _attach_existing(
            self,
            cmd: ApplyDocumentCommand,
            document: Document,
    ) -> None:

        if not cmd.target_record_id:
            raise RuntimeError("Missing target record")

        record = self._records.get(
            organization_id=cmd.organization_id,
            record_id=cmd.target_record_id,
        )

        if not record:
            raise RuntimeError("Target record not found")

        # 🔹 Seller validation
        if document.seller_nip:
            seller = self._company_eval.evaluate_from_tax(
                organization_id=cmd.organization_id,
                actor_user_id=cmd.actor_user_id,
                input_tax_number=document.seller_nip,
                role=CompanyType.SELLER,
                mode=EvaluateMode.NO_CREATE,
            )

            if record.seller_id != seller.id:
                raise RuntimeError("Seller mismatch")

        # ============================================================
        # 1️⃣ MOVE TO RAW (technical)
        # ============================================================

        org_root = cfg.WORK_DIR / str(cmd.organization_id)

        raw_relative = self._files.move_to_raw(
            root=org_root,
            file_path=org_root / document.file_path,
        )

        updated_doc = replace(
            document,
            file_path=raw_relative.as_posix(),
        )

        self._documents.update(updated_doc)

        # ============================================================
        # 2️⃣ ATTACH
        # ============================================================

        self._documents.attach_to_record(
            organization_id=cmd.organization_id,
            document_id=document.id,
            record_id=record.id,
        )

        # ============================================================
        # 3️⃣ SYNC (business location)
        # ============================================================

        refreshed_record = self._records.get(
            organization_id=cmd.organization_id,
            record_id=record.id,
        )
        if refreshed_record:
            self._file_workflow_service.sync(
                organization_id=cmd.organization_id,
                record=refreshed_record,
            )

    def _skip(self, document: Document) -> None:
        org_root = cfg.WORK_DIR / str(document.organization_id)

        target_relative =self._files.move_to_skipped(
            root=org_root,
            file_path=org_root /document.file_path,
        )

        updated = replace(
            document,
            file_path=target_relative.as_posix(),
        )
        self._documents.update(updated)


    def _delete(self, document: Document) -> None:

        org_root = cfg.WORK_DIR / str(document.organization_id)

        self._documents.delete(
            organization_id=document.organization_id,
            document_id=document.id,
        )

        self._files.move_to_trash(
            root=org_root,
            file_path=org_root / document.file_path,
        )

