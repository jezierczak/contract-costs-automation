import hashlib
import logging
import mimetypes
from dataclasses import replace
from pathlib import Path
from uuid import UUID

import contract_costs.config as cfg

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.document import Document, DocumentType, DocumentSource
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.repository.financial_record_repository import FinancialRecordRepository

logger = logging.getLogger(__name__)


class MigrateScanFilenameService:

    def __init__(
        self,
        record_repository: FinancialRecordRepository,
        document_repository: DocumentRepository,
    ) -> None:
        self._records = record_repository
        self._documents = document_repository

    # ============================================================
    # ENTRY POINT
    # ============================================================

    def migrate(
        self,
        *,
        organization_id: UUID,
        actor_user_id: UUID,
        dry_run: bool = True,
    ) -> None:

        logger.info("Starting scan_filename migration (dry_run=%s)", dry_run)

        records = self._records.list_all(organization_id=organization_id)

        org_root = cfg.WORK_DIR / str(organization_id)

        migrated = 0
        skipped = 0
        missing_files = 0

        for record in records:

            # if not record.scan_filename:
            #     continue
            #
            # file_path = record.scan_filename
            # # abs_path = org_root / file_path
            # raw_value = record.scan_filename
            # path = Path(raw_value)
            #
            # if path.is_absolute():
            #     abs_path = path
            # elif raw_value.startswith(str(cfg.WORK_DIR)):
            #     abs_path = Path(raw_value)
            # else:
            #     abs_path = (cfg.WORK_DIR / str(organization_id) / raw_value).resolve()
            # # -------------------------------------------------
            # CHECK FILE EXISTS
            # -------------------------------------------------
            #
            # if not abs_path.exists():
            #     logger.error(
            #         "Missing file on disk for record %s: %s",
            #         record.id,
            #         abs_path,
            #     )
            #     missing_files += 1
            #     continue

            # -------------------------------------------------
            # CHECK IF DOCUMENT ALREADY EXISTS
            # -------------------------------------------------

            existing_docs = self._documents.list_by_record_id(
                organization_id=organization_id,
                record_id=record.id,
            )
            #
            # if any(doc.file_path == file_path for doc in existing_docs):
            #     logger.warning(
            #         "Document already exists for record %s (%s)",
            #         record.id,
            #         file_path,
            #     )
            #     skipped += 1
            #     continue
            #
            # filename = Path(file_path).name

            # logger.info(
            #     "Migrating record %s → document %s",
            #     record.reference,
            #     filename,
            # )

            if dry_run:
                continue

            # -------------------------------------------------
            # CREATE DOCUMENT
            # -------------------------------------------------

            # file_hash = _calculate_hash(abs_path)
            # mime_type, _ = mimetypes.guess_type(filename)
            # size = abs_path.stat().st_size
            #
            # document = Document(
            #     id=new_uuid(),
            #     organization_id=organization_id,
            #     filename=filename,
            #     file_path=file_path,
            #     document_type=DocumentType.INVOICE,
            #     financial_record_id=record.id,
            #     parsed_payload=None,
            #     created_at=utc_now(),
            #     created_by_user_id=actor_user_id,
            #     seller_nip=None,
            #     updated_at=None,
            #     updated_by_user_id=None,
            #     document_source=DocumentSource.PDF,
            #     document_number=record.reference,
            #     file_hash=file_hash,
            #     mime_type=mime_type,
            #     size=size,
            # )

            # self._documents.add(document)
            #
            # # -------------------------------------------------
            # # CLEAR scan_filename
            # # -------------------------------------------------
            #
            # self._records.update(
            #     replace(record, scan_filename=None)
            # )

            migrated += 1

        logger.info("Migration finished.")
        logger.info("Migrated: %s", migrated)
        logger.info("Skipped: %s", skipped)
        logger.info("Missing files: %s", missing_files)



def _calculate_hash(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()