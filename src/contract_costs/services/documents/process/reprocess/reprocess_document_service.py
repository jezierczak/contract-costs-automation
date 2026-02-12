
from contract_costs.action_bus.action_bus import ActionBus
from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.services.documents.process.dto.process_document_command import ProcessDocumentCommand
from contract_costs.services.documents.process.reprocess.reprocess_document_command import ReprocessDocumentCommand
from contract_costs.services.documents.process.process_document_service import ProcessDocumentService


class ReprocessDocumentService(ActionHandler[ReprocessDocumentCommand,None]):

    def __init__(
        self,
        documents: DocumentRepository,
        action_bus: ActionBus,
        process_document_service: ProcessDocumentService,
    ) -> None:
        self._documents = documents
        self._action_bus = action_bus
        self._process_document_service = process_document_service

    def execute(self, cmd: ReprocessDocumentCommand) -> None:

        document = self._documents.get(
            organization_id=cmd.organization_id,
            document_id=cmd.document_id,
        )

        if not document:
            raise RuntimeError("Document not found")

        if document.financial_record_id:
            raise RuntimeError("Cannot reprocess document already assigned to record")

        # Delegujemy do istniejącego flow
        self._action_bus.execute(
            action=ProcessDocumentCommand(
                organization_id=cmd.organization_id,
                actor_user_id=cmd.actor_user_id,
                document_id=cmd.document_id,
                force=cmd.force,
            ),
            handler=self._process_document_service
        )
