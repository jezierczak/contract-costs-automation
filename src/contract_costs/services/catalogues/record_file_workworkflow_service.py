import logging
from dataclasses import replace
from pathlib import Path
from uuid import UUID

from contract_costs.model.company import CompanyType
from contract_costs.model.financial_record import FinancialRecord, FinancialRecordStatus
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.services.catalogues.record_file_organizer import RecordFileOrganizer

import contract_costs.config as cfg

logger = logging.getLogger(__name__)

class RecordFileWorkflowService:

    def __init__(
        self,
        company_repository: CompanyRepository,
        file_organizer: RecordFileOrganizer,
        document_repository: DocumentRepository,
    ) -> None:
        self._company_repository = company_repository
        self._file_organizer = file_organizer
        self._document_repository = document_repository

    # ============================================================
    # SYNC
    # ============================================================

    def sync(
        self,
        *,
        organization_id: UUID,
        record: FinancialRecord,
    ) -> None:

        if not record.documents:
            return

        org_root = cfg.WORK_DIR / str(organization_id)

        buyer = (
            self._company_repository.get(
                organization_id=organization_id,
                company_id=record.buyer_id,
            )
            if record.buyer_id else None
        )

        seller = (
            self._company_repository.get(
                organization_id=organization_id,
                company_id=record.seller_id,
            )
            if record.seller_id else None
        )

        for idx,document in enumerate(record.documents):

            current_relative = Path(document.file_path)
            current_path = org_root / current_relative

            if not current_path.exists():
                logger.warning(
                    "Document file missing (record=%s, doc=%s): %s",
                    record.id,
                    document.id,
                    current_path,
                )
                continue

            # ===============================
            # DELETED
            # ===============================

            if record.status == FinancialRecordStatus.DELETED:
                target_relative = self._file_organizer.move_to_trash(
                    root=org_root,
                    file_path=current_path,
                )

            # ===============================
            # DRAFT
            # ===============================

            elif not buyer or not seller:
                target_relative = self._file_organizer.move_to_draft(
                    root=org_root,
                    file_path=current_path,
                )

            # ===============================
            # COST
            # ===============================

            elif buyer.role == CompanyType.OWN:
                target_relative = self._file_organizer.move_to_owner(
                    root=org_root,
                    file_path=current_path,
                    kind="cost",
                    owner=buyer,
                    issue_date=record.invoice_date,
                    client_name=seller.name,
                    record_ref_number=record.reference,
                )

            # ===============================
            # REVENUE
            # ===============================

            elif seller.role == CompanyType.OWN:
                target_relative = self._file_organizer.move_to_owner(
                    root=org_root,
                    file_path=current_path,
                    kind="revenue",
                    owner=seller,
                    issue_date=record.invoice_date,
                    client_name=buyer.name,
                    record_ref_number=record.reference,
                )

            # ===============================
            # FALLBACK
            # ===============================

            else:
                target_relative = self._file_organizer.move_to_draft(
                    root=org_root,
                    file_path=current_path,
                )

            # ===============================
            # NO CHANGE
            # ===============================

            if target_relative.as_posix() == document.file_path:
                continue
            new_filename = target_relative.name
            # update document path in memory
            updated = replace(
                document,
                file_path=target_relative.as_posix(),
                filename=new_filename,
            )

            self._document_repository.update(updated)

            record.documents[idx] = updated

            logger.info(
                "Document moved: %s → %s",
                current_path,
                org_root / target_relative,
            )
