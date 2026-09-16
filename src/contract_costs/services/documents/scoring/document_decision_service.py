from uuid import UUID

from contract_costs.model.document import Document
from contract_costs.services.documents.scoring.document_decision import DocumentDecision, DocumentDecisionResult
from contract_costs.services.documents.scoring.find_matching_record_service import FindMatchingRecordService, MatchMode
from contract_costs.unit_of_work import UnitOfWork


import logging
logger = logging.getLogger(__name__)

class DocumentDecisionService:
    HIGH_CONFIDENCE = 80
    MEDIUM_CONFIDENCE = 60

    def __init__(self, matching_service: FindMatchingRecordService):
        self._matching_service = matching_service

    def decide(
            self,
            *,
            actor_user_id: UUID,
            document: Document,
            uow: UnitOfWork
    ) -> DocumentDecisionResult:

        decision = DocumentDecision.MANUAL
        record_id = None

        if not document.scoring:
            return DocumentDecisionResult(decision)

        score = document.scoring.score

        if score < self.MEDIUM_CONFIDENCE:
            return DocumentDecisionResult(decision)

        reference = document.document_number
        seller_nip = document.seller_nip

        # =====================
        # STRICT
        # =====================
        strict_matches = self._matching_service.find(
            document=document,
            uow=uow,
            actor_user_id=actor_user_id,
            mode=MatchMode.STRICT
        )

        # =====================
        # CANDIDATES (ZAWSZE!)
        # =====================
        candidate_matches = self._matching_service.find(
            document=document,
            uow=uow,
            actor_user_id=actor_user_id,
            mode=MatchMode.CANDIDATE
        )

        # =====================
        # DECISION
        # =====================
        if score >= self.HIGH_CONFIDENCE:

            if len(strict_matches) == 1:
                decision = DocumentDecision.AUTO_ATTACH
                record_id = strict_matches[0]

            elif len(strict_matches) == 0:

                if len(candidate_matches) == 0:
                    decision = DocumentDecision.AUTO_CREATE

                else:
                    decision = DocumentDecision.MANUAL

            else:
                decision = DocumentDecision.MANUAL

        return self._log_and_return(
            decision,
            document,
            score,
            candidate_matches,
            record_id
        )

    @staticmethod
    def _log_and_return(
        decision: DocumentDecision,
        document: Document,
        score: int,
        matches: list[UUID],
        record_id: UUID | None = None,
    ) -> DocumentDecisionResult:

        logger.info(
            "[DECISION] %s | doc=%s | score=%s | matches=%s | record_id=%s",
            decision,
            document.id,
            score,
            matches,
            record_id,
        )

        return DocumentDecisionResult(
            decision=decision,
            record_id=record_id,
        )