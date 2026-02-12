from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.services.documents.process.delete.delete_document_command import DeleteDocumentCommand


class DeleteDocumentService(ActionHandler[DeleteDocumentCommand,None]):

    def __init__(
        self,
        documents: DocumentRepository,
    ) -> None:
        self._documents = documents

    def execute(self, cmd: DeleteDocumentCommand) -> None:

        document = self._documents.get(
            organization_id=cmd.organization_id,
            document_id=cmd.document_id,
        )

        if not document:
            raise RuntimeError("Document not found")

        if document.financial_record_id:
            raise RuntimeError("Cannot delete document assigned to record")

        self._documents.delete(
            organization_id=cmd.organization_id,
            document_id=cmd.document_id,
        )
