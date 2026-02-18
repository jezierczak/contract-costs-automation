import json
import logging
from dataclasses import asdict, replace
from datetime import date
from decimal import Decimal
from enum import Enum

import contract_costs.config as cfg
from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.documents.exeptions import DocumentFatalError
from contract_costs.services.documents.process.dto.process_document_command import ProcessDocumentCommand
from contract_costs.services.documents.process.parse_document_from_file import ParseDocumentFromFileService
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ProcessDocumentService(ActionHandler[ProcessDocumentCommand, None]):

    def __init__(
        self,
        # document_repository: DocumentRepository,
        parse_service: ParseDocumentFromFileService,
    ):
        # self._documents = document_repository
        self._parser = parse_service

    def execute(self, *, action: ProcessDocumentCommand, uow: UnitOfWork) -> None:
        doc_repo = uow.documents
        document = doc_repo.get(
            organization_id=action.organization_id,
            document_id=action.document_id,
        )

        if not document:
            raise ValueError("Document not found")

        if document.parsed_payload is not None and not action.force:
            logger.info("Document already parsed. Use --force to reprocess. Document id: %s", document.id)

        if action.force:
            logger.info("Force reprocessing document %s", document.id)

        org_root = cfg.WORK_DIR / str(action.organization_id)
        file_path = org_root / document.file_path

        if document.document_source is None:
            raise RuntimeError("Document source missing")

        try:
            parse_result = self._parser.execute(
                file_path=file_path,
                source=document.document_source,
            )
        except DocumentFatalError as e:
            logger.exception("Fatal parsing error for document %s", document.id)
            try:
                failed_path = DocumentFileOrganizer.move_to_failed(
                    root=org_root,
                    file_path=file_path,
                    reason="parse_error",
                )
                document.file_path = str(failed_path)
                doc_repo.update(document)
            except Exception:
                logger.exception("Failed to move document to failed directory")
            raise e

        try:
            raw_path = DocumentFileOrganizer.move_to_raw(
                root=org_root,
                file_path=file_path,
            )
        except Exception:
            logger.exception("Failed to move document to raw directory")
            try:
                failed_path = DocumentFileOrganizer.move_to_failed(
                    root=org_root,
                    file_path=file_path,
                    reason="move_error",
                )
                document.file_path = str(failed_path)
                doc_repo.update(document)
            except Exception:
                logger.exception("Failed to move document to failed after move error")
            raise

        updated = replace(
            document,
            parsed_payload=json.loads(json.dumps(asdict(parse_result), default=self._serialize)),
            document_number=parse_result.record.reference,
            seller_nip=parse_result.seller.tax_number,
            document_type=parse_result.document_type,
            file_path=str(raw_path),
        )

        doc_repo.update(updated)

    @staticmethod
    def _serialize(obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, date):
            return obj.isoformat()
        return obj
