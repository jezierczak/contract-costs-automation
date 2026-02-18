from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer
from contract_costs.services.documents.process.delete.delete_document_command import DeleteDocumentCommand
from contract_costs.unit_of_work import UnitOfWork
import contract_costs.config as cfg

class DeleteDocumentService(ActionHandler[DeleteDocumentCommand, None]):

    # def __init__(
    #     self,
    #     documents: DocumentRepository,
    # ) -> None:
    #     self._documents = documents

    def execute(self, *, action: DeleteDocumentCommand, uow: UnitOfWork) -> None:
        doc_repo = uow.documents
        document = doc_repo.get(
            organization_id=action.organization_id,
            document_id=action.document_id,
        )

        if not document:
            raise RuntimeError("Document not found")

        if document.financial_record_id:
            raise RuntimeError("Cannot delete document assigned to record")

        doc_repo.delete(
            organization_id=action.organization_id,
            document_id=action.document_id,
        )
        file_path = document.file_path

        uow.add_post_commit_hook(
            lambda: DocumentFileOrganizer.delete_file(
                root=cfg.WORK_DIR / str(action.organization_id),
                relative_path=file_path,
            )
        )
