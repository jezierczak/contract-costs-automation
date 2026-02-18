from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.documents.process.dto.process_document_command import ProcessDocumentCommand
from contract_costs.services.documents.process.process_document_service import ProcessDocumentService
from contract_costs.services.documents.process.reprocess.reprocess_document_command import ReprocessDocumentCommand
from contract_costs.unit_of_work import UnitOfWork



class ReprocessDocumentService(ActionHandler[ReprocessDocumentCommand, None]):

    def __init__(
        self,
        # documents: DocumentRepository,
        # action_bus: ActionBus,
        process_document_service: ProcessDocumentService,
    ) -> None:
        # self._documents = documents
        # self._action_bus = action_bus
        self._process_document_service = process_document_service

    def execute(self, *, action: ReprocessDocumentCommand, uow: UnitOfWork) -> None:
        document_repo = uow.documents

        document = document_repo.get(
            organization_id=action.organization_id,
            document_id=action.document_id,
        )

        if not document:
            raise RuntimeError("Document not found")

        if document.financial_record_id:
            raise RuntimeError("Cannot reprocess document already assigned to record")

        process_action = ProcessDocumentCommand(
            organization_id=action.organization_id,
            actor_user_id=action.actor_user_id,
            document_id=action.document_id,
            force=action.force,
        )

        self._process_document_service.execute(
            action=process_action,
            uow=uow,
        )

