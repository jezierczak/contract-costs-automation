import logging

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.documents.query.document_list_item_dto import DocumentListItemDto
from contract_costs.services.documents.query.list_docuemnts_query_command import ListDocumentsQueryCommand
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class ListDocumentsQueryService(ActionHandler[ListDocumentsQueryCommand, list[DocumentListItemDto]]):

    # def __init__(
    #     self,
    #     document_repository: DocumentRepository,
    # ) -> None:
    #     self._documents = document_repository

    def execute(
        self,
        *,
        action: ListDocumentsQueryCommand,
        uow: UnitOfWork,
    ) -> list[DocumentListItemDto]:
        documents_repo=uow.documents
        documents = documents_repo.list_filtered(
            organization_id=action.organization_id,
            has_payload=action.has_payload,
            has_record=action.has_record,
            document_source=action.source,
        )

        documents = sorted(
            documents,
            key=lambda d: d.created_at,
            reverse=True,
        )

        result: list[DocumentListItemDto] = []

        for d in documents:
            file_name = self._extract_file_name(d.file_path)

            result.append(
                DocumentListItemDto(
                    document_id=d.id,
                    file_name=file_name,
                    document_source=d.document_source.value if d.document_source else "unknown",
                    document_type=d.document_type.value if d.document_type else "unknown",
                    document_number=d.document_number,
                    seller_nip=d.seller_nip,
                    has_payload=d.parsed_payload is not None,
                    has_record=d.financial_record_id is not None,
                    created_at=d.created_at,
                    file_path=d.file_path,
                )
            )

        logger.info(
            "ListDocumentsQueryService returned %s documents for org=%s",
            len(result),
            action.organization_id,
        )

        return result

    @staticmethod
    def _extract_file_name(file_path: str | None) -> str:
        if not file_path:
            return "unknown"

        return file_path.split("/")[-1].split("\\")[-1]
