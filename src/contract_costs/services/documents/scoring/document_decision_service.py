from uuid import UUID

from contract_costs.model.document import Document
from contract_costs.services.documents.scoring.document_decision import DocumentDecision, DocumentDecisionResult
from contract_costs.services.documents.scoring.find_matching_record_service import FindMatchingRecordService
from contract_costs.unit_of_work import UnitOfWork


class DocumentDecisionService:
    HIGH_CONFIDENCE = 80
    MEDIUM_CONFIDENCE = 60

    def __init__(self,matching_service:FindMatchingRecordService):
        self._matching_service=matching_service

    def decide(
            self,
            *,
            actor_user_id: UUID,
            document: Document,
            uow: UnitOfWork
    ) -> DocumentDecisionResult:

        if not document.scoring:
            return DocumentDecisionResult(DocumentDecision.MANUAL)

        score = document.scoring.score

        if score < self.MEDIUM_CONFIDENCE:
            return DocumentDecisionResult(DocumentDecision.MANUAL)

        reference = document.document_number
        seller_nip = document.seller_nip

        if not reference or not seller_nip:
            if score >= self.HIGH_CONFIDENCE:
                return DocumentDecisionResult(DocumentDecision.AUTO_CREATE)
            return DocumentDecisionResult(DocumentDecision.MANUAL)

        existing_id = self._matching_service.find(
            document=document,
            uow=uow,
            actor_user_id=actor_user_id
        )

        if score >= self.HIGH_CONFIDENCE:
            if existing_id:
                return DocumentDecisionResult(
                    decision=DocumentDecision.AUTO_ATTACH,
                    record_id=existing_id,
                )
            return DocumentDecisionResult(DocumentDecision.AUTO_CREATE)

        return DocumentDecisionResult(DocumentDecision.MANUAL)