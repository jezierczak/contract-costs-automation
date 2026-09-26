import logging
from datetime import date

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
            document_status=action.status,
        )

        documents = sorted(
            documents,
            # created_at ma sekundowa precyzje - paczka z KSeF laduje w tej samej sekundzie
            key=lambda d: (d.created_at, d.document_number or "", d.filename or ""),
            reverse=True,
        )

        result: list[DocumentListItemDto] = []

        for d in documents:
            file_name = self._extract_file_name(d.file_path)
            payload = d.parsed_payload if isinstance(d.parsed_payload, dict) else {}
            seller = self._as_dict(payload.get("seller"))
            buyer = self._as_dict(payload.get("buyer"))
            record = self._as_dict(payload.get("record"))

            result.append(
                DocumentListItemDto(
                    document_id=d.id,
                    file_name=file_name,
                    document_source=d.document_source.value if d.document_source else "unknown",
                    document_type=d.document_type.value if d.document_type else "unknown",
                    document_number=d.document_number,
                    seller_nip=d.seller_nip,
                    document_status=d.document_status.value,
                    financial_record_id=d.financial_record_id,
                    has_payload=d.parsed_payload is not None,
                    has_record=d.financial_record_id is not None,
                    confidence_score=d.scoring.score if d.scoring else None,
                    confidence_breakdown=d.scoring.breakdown if d.scoring else None,
                    created_at=d.created_at,
                    file_path=d.file_path,
                    seller_name=seller.get("name") or None,
                    buyer_name=buyer.get("name") or None,
                    buyer_nip=buyer.get("tax_number") or None,
                    invoice_date=self._parse_date(record.get("invoice_date")),
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

    @staticmethod
    def _as_dict(value) -> dict:
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _parse_date(value) -> date | None:
        if not value:
            return None
        try:
            return date.fromisoformat(str(value)[:10])
        except ValueError:
            return None
