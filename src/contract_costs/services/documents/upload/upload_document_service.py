import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Callable
from uuid import UUID
import mimetypes

from contract_costs.action_bus.handler_registry import handles
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.document import Document, DocumentSource
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.queue.document_queue import document_queue
from contract_costs.services.documents.upload.dto.upload_document_command import UploadDocumentCommand
from contract_costs.services.workers.dto.document_process_queue_item import DocumentProcessQueueItem

import contract_costs.config as cfg

logger = logging.getLogger(__name__)

@handles(UploadDocumentCommand)
class UploadDocumentService:

    def __init__(
        self,
        document_repository: DocumentRepository,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._documents = document_repository
        self._clock = clock
        self._id_generator = id_generator

    def execute(self, cmd: UploadDocumentCommand) -> UUID | None:

        file_path: Path = cmd.file_path

        if not file_path.exists():
            raise FileNotFoundError(file_path)

        file_hash = self._calculate_hash(file_path)
        org_root = cfg.WORK_DIR / str(cmd.organization_id)

        # 🔁 idempotencja
        if self._documents.exists_by_hash(
                organization_id=cmd.organization_id,
                file_hash=file_hash,
        ):
            logger.info(
                "Document already exists (hash=%s), moving to duplicates",
                file_hash,
            )

            DocumentFileOrganizer.move_to_duplicates(
                root=org_root,
                file_path=file_path,
            )
            return None



        # 1 resolve source (PO ROZSZERZENIU)
        document_type = self._resolve_source(file_path)
        size = file_path.stat().st_size
        # 2 move → processing
        processing_path = DocumentFileOrganizer.move_to_processing(
            root=org_root,
            file_path=file_path,
        )

        now = self._clock()
        document_id = self._id_generator()
        mime_type = self._resolve_mime_type(processing_path)


        document = Document(
            id=document_id,
            organization_id=cmd.organization_id,
            financial_record_id=None,

            document_source=document_type,

            document_type=None,
            document_number=None,
            seller_nip=None,
            parsed_payload=None,

            file_hash=file_hash,
            file_path=str(processing_path),  # ⬅️ ważne!
            filename=processing_path.name,
            mime_type=mime_type,
            size=size,

            created_at=now,
            created_by_user_id=cmd.actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
        )

        self._documents.add(document)

        # 🚀 enqueue
        document_queue.put(
            DocumentProcessQueueItem(
                cmd.organization_id,
                cmd.actor_user_id,
                document_id,
            )
        )

        return document_id

    @staticmethod
    def _calculate_hash(file_path: Path) -> str:
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    # =========================================================

    @staticmethod
    def _resolve_source(file_path: Path) -> DocumentSource:
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            return DocumentSource.PDF
        if ext == ".xml":
            return DocumentSource.KSEF
        if ext in {".jpg", ".jpeg", ".png"}:
            return DocumentSource.IMAGE

        raise ValueError(f"Unsupported file extension: {ext}")

    @staticmethod
    def _resolve_mime_type(file_path: Path) -> str | None:
        mime, _ = mimetypes.guess_type(str(file_path))
        return mime
