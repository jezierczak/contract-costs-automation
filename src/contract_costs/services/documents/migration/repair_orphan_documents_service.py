import logging
from dataclasses import dataclass, replace
from pathlib import Path
from uuid import UUID

import contract_costs.config as cfg
from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.model.document import DocumentStatus
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.documents.migration.repair_orphan_documents_command import (
    RepairOrphanDocumentsCommand,
)
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class OrphanDocumentFix:
    document_id: UUID
    document_number: str | None
    old_path: str
    new_path: str | None
    # plik nie istnieje – status zmieniamy, pliku nie ruszamy
    file_missing: bool


class RepairOrphanDocumentsService(
    ActionHandler[RepairOrphanDocumentsCommand, list[OrphanDocumentFix]]
):
    """
    Dokumenty APPLIED bez rekordu – zostają, gdy rekord zniknie z bazy fizycznie
    (FK documents.financial_record_id ma ON DELETE SET NULL, status się nie zmienia).
    Naprawa jak przy „odepnij”: plik wraca do katalogu roboczego, status READY,
    dokument znów można przypisać.
    Bez `apply` tylko zwraca listę.
    """

    def __init__(self, work_dir: Path | None = None) -> None:
        self._work_dir = work_dir

    def execute(
        self,
        *,
        action: RepairOrphanDocumentsCommand,
        uow: UnitOfWork,
    ) -> list[OrphanDocumentFix]:
        org_root = (self._work_dir or cfg.WORK_DIR) / str(action.organization_id)
        orphans = uow.documents.list_filtered(
            organization_id=action.organization_id,
            has_record=False,
            document_status=DocumentStatus.APPLIED,
        )

        fixes = []
        for document in orphans:
            file_missing = not (org_root / document.file_path).exists()
            new_path = None
            if action.apply:
                if not file_missing:
                    new_path = DocumentFileOrganizer.move_to_raw(
                        root=org_root,
                        file_path=org_root / document.file_path,
                    ).as_posix()
                uow.documents.update(replace(
                    document,
                    file_path=new_path or document.file_path,
                    document_status=DocumentStatus.READY,
                ))
                logger.info("Orphan document %s back to READY (%s)", document.id, new_path)

            fixes.append(OrphanDocumentFix(
                document_id=document.id,
                document_number=document.document_number,
                old_path=document.file_path,
                new_path=new_path,
                file_missing=file_missing,
            ))
        return fixes
