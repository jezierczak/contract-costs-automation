import logging

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.repository.document_repository import DocumentRepository
from contract_costs.services.documents.query.document_list_item_dto import DocumentListItemDto
from contract_costs.services.documents.query.list_docuemnts_query_command import ListDocumentsQueryCommand

logger = logging.getLogger(__name__)


class ListDocumentsQueryService(ActionHandler[ListDocumentsQueryCommand,list[DocumentListItemDto]]):

    def __init__(
        self,
        document_repository: DocumentRepository,
    ) -> None:
        self._documents = document_repository

    def execute(
        self,
        cmd: ListDocumentsQueryCommand,
    ) -> list[DocumentListItemDto]:

        documents = self._documents.list_filtered(
            organization_id=cmd.organization_id,
            has_payload=cmd.has_payload,
            has_record=cmd.has_record,
            document_source=cmd.source,
        )

        # Bezpieczne sortowanie (gdyby repo nie sortowało)
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
            cmd.organization_id,
        )

        return result

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _extract_file_name(file_path: str | None) -> str:
        if not file_path:
            return "unknown"

        return file_path.split("/")[-1].split("\\")[-1]
