from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.documents.query.dto.document_file_dto import DocumentFileDto
from contract_costs.services.documents.query.dto.get_document_file_query import GetDocumentFileQuery
import contract_costs.config as cfg

class GetDocumentFileQueryService(
    ActionHandler[GetDocumentFileQuery, DocumentFileDto]
):

    def execute(self, *, action, uow):

        repo = uow.documents

        document = repo.get(
            organization_id=action.organization_id,
            document_id=action.document_id,
        )

        if not document:
            raise ValueError("Document not found")

        org_root = cfg.WORK_DIR / str(action.organization_id)

        return DocumentFileDto(
            file_path=str(org_root / document.file_path),
            ksef_number=document.ksef_number,
        )