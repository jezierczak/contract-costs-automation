import json
import logging
from dataclasses import asdict
from datetime import date
from decimal import Decimal
from enum import Enum


import contract_costs.config as cfg
from contract_costs.action_bus.action_handler import ActionHandler
# from contract_costs.action_bus.handler_registry import handles
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.documents.exeptions import DocumentFatalError
from contract_costs.services.documents.process.dto.process_document_command import (
    ProcessDocumentCommand,
)
from contract_costs.services.documents.process.parse_document_from_file import (
    ParseDocumentFromFileService,
)

logger = logging.getLogger(__name__)

# @handles(ProcessDocumentCommand)
class ProcessDocumentService(ActionHandler[ProcessDocumentCommand,None]):

    def __init__(
        self,
        document_repository: DocumentRepository,
        parse_service: ParseDocumentFromFileService,
    ):
        self._documents = document_repository
        self._parser = parse_service

    def execute(self, cmd: ProcessDocumentCommand) -> None:

        document = self._documents.get(
            organization_id=cmd.organization_id,
            document_id=cmd.document_id,
        )

        if not document:
            raise ValueError("Document not found")

        # idempotencja
        if document.parsed_payload is not None and not cmd.force:
            logger.info("Document already parsed. Use --force to reprocess. Document id: %s",document.id)

        if cmd.force:
            logger.info("Force reprocessing document %s", document.id)

        org_root = cfg.WORK_DIR / str(cmd.organization_id)
        file_path = org_root / document.file_path  # zakładamy ścieżkę relative

        # =====================================================
        # 1️⃣ PARSE
        # =====================================================

        if document.document_source is None:
            raise RuntimeError("Document source missing")

        try:
            parse_result = self._parser.execute(
                file_path=file_path,
                source=document.document_source,
            )
        except DocumentFatalError as e:
            logger.exception(
                "Fatal parsing error for document %s", document.id
            )

            # move → failed
            try:
                failed_path = DocumentFileOrganizer.move_to_failed(
                    root=org_root,
                    file_path=file_path,
                    reason="parse_error",
                )
                document.file_path = str(failed_path)
                self._documents.update(document)
            except Exception:
                logger.exception("Failed to move document to failed directory")

            raise e

        # =====================================================
        # 2️⃣ MOVE → RAW
        # =====================================================
        try:
            raw_path = DocumentFileOrganizer.move_to_raw(
                root=org_root,
                file_path=file_path,
            )
        except Exception as e:
            logger.exception("Failed to move document to raw directory")

            # jeśli nie udało się przenieść do raw → traktujemy jako fail
            try:
                failed_path = DocumentFileOrganizer.move_to_failed(
                    root=org_root,
                    file_path=file_path,
                    reason="move_error",
                )
                document.file_path = str(failed_path)
                self._documents.update(document)
            except Exception:
                logger.exception("Failed to move document to failed after move error")

            raise

        # =====================================================
        # 3️⃣ UPDATE DOCUMENT
        # =====================================================
        document.parsed_payload = json.loads(
            json.dumps(asdict(parse_result), default=self._serialize)
        )

        document.document_number = parse_result.record.reference
        document.seller_nip = parse_result.seller.tax_number
        document.document_type = parse_result.document_type
        document.file_path = str(raw_path)

        self._documents.update(document)

        logger.info(
            "Document processed successfully (doc=%s type=%s)",
            document.id,
            document.document_type,
        )

    # =====================================================
    # SERIALIZER
    # =====================================================

    @staticmethod
    def _serialize(obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        return obj
