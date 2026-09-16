from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.documents.process.unattach.unattach_document_command import UnattachDocumentCommand
from contract_costs.unit_of_work import UnitOfWork
import contract_costs.config as cfg


class UnattachDocumentService(ActionHandler[UnattachDocumentCommand, None]):
    def __init__(self, document_file_organizer: DocumentFileOrganizer) -> None:
        self._document_file_organizer = document_file_organizer

    def execute(self, *, action: UnattachDocumentCommand, uow: UnitOfWork) -> None:
        doc_repo = uow.documents

        document = doc_repo.get(
            organization_id=action.organization_id,
            document_id=action.document_id,
        )

        if not document:
            raise RuntimeError("Document not found")

        if not document.financial_record_id:
            raise RuntimeError("Document is not attached")

        org_root = cfg.WORK_DIR / str(action.organization_id)

        # =====================
        # 1️⃣ MOVE FILE
        # =====================
        raw_relative = self._document_file_organizer.move_to_raw(
            root=org_root,
            file_path=org_root / document.file_path,
        )

        # =====================
        # 2️⃣ DB UPDATE
        # =====================
        doc_repo.unattach_from_record(
            organization_id=action.organization_id,
            document_id=action.document_id,
            file_path=raw_relative.as_posix(),
        )
