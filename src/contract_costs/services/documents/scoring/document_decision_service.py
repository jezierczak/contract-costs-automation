from contract_costs.model.document import Document, DocumentSource
from contract_costs.services.common.resolve_utils import normalize_tax_number
from contract_costs.services.companies.validators.company import CompanyValidator
from contract_costs.services.documents.scoring.document_decision import DocumentDecision, DocumentDecisionResult
from contract_costs.services.documents.scoring.find_matching_record_service import (
    FindMatchingRecordService,
    MatchResult,
)
from contract_costs.unit_of_work import UnitOfWork


import logging
logger = logging.getLogger(__name__)


class DocumentDecisionService:
    """
    Co zrobić z dokumentem zaraz po imporcie:
    - jedno dopasowanie ścisłe (numer + sprzedawca) → przypnij,
    - brak dopasowań i znani kontrahenci → utwórz rekord,
    - wszystko inne (kilka dopasowań, kandydaci po kwotach, nieznany sprzedawca
      lub nabywca) → ręcznie.
    KSeF jest pewny, więc decyzja nie zależy od scoringu; OCR wymaga HIGH_CONFIDENCE.
    """
    HIGH_CONFIDENCE = 80

    def __init__(self, matching_service: FindMatchingRecordService):
        self._matching_service = matching_service

    def decide(self, *, document: Document, uow: UnitOfWork) -> DocumentDecisionResult:
        if not document.scoring:
            return DocumentDecisionResult(DocumentDecision.MANUAL)

        score = document.scoring.score
        is_ksef = document.document_source == DocumentSource.KSEF
        if not is_ksef and score < self.HIGH_CONFIDENCE:
            return self._log_and_return(DocumentDecisionResult(DocumentDecision.MANUAL), document, None)

        result = self._matching_service.find(document=document, uow=uow)

        if len(result.strict) == 1:
            decision = DocumentDecisionResult(DocumentDecision.AUTO_ATTACH, result.strict[0].record.id)
        elif result.matches:
            decision = DocumentDecisionResult(DocumentDecision.MANUAL)
        elif not self._parties_known(result):
            # nieznany sprzedawca/nabywca trafiłby na UNKNOWN_* – użytkownik wybiera firmę
            decision = DocumentDecisionResult(DocumentDecision.MANUAL)
        else:
            decision = DocumentDecisionResult(DocumentDecision.AUTO_CREATE)

        return self._log_and_return(decision, document, result)

    @staticmethod
    def _parties_known(result: MatchResult) -> bool:
        def known(company, tax_number) -> bool:
            return company is not None or CompanyValidator.is_trusted_tax_number(normalize_tax_number(tax_number))

        return known(result.seller, result.seller_tax_number) and known(result.buyer, result.buyer_tax_number)

    @staticmethod
    def _log_and_return(
        decision: DocumentDecisionResult,
        document: Document,
        result: MatchResult | None,
    ) -> DocumentDecisionResult:
        logger.info(
            "[DECISION] %s | doc=%s | score=%s | matches=%s | record_id=%s",
            decision.decision,
            document.id,
            document.scoring.score if document.scoring else None,
            [(m.record.reference, sorted(r.value for r in m.reasons)) for m in result.matches] if result else [],
            decision.record_id,
        )
        return decision
