from uuid import UUID

from contract_costs.model.company import CompanyType
from contract_costs.model.document import Document
from contract_costs.services.companies.company_evaluate_orchestrator import EvaluateMode, CompanyEvaluateOrchestrator
from contract_costs.unit_of_work import UnitOfWork
import logging

logger = logging.getLogger(__name__)

class FindMatchingRecordService:

    def __init__(self, company_evaluator: CompanyEvaluateOrchestrator):
        self._company_eval = company_evaluator

    def find(
        self,
        *,
        document: Document,
        actor_user_id: UUID,
        uow: UnitOfWork,
    ) -> UUID | None:

        reference = document.document_number
        seller_nip = document.seller_nip
        score = document.scoring.score if document.scoring else None

        if not reference or not seller_nip:
            logger.debug(
                "[MATCH] Skipped | doc=%s | score=%s | missing reference or seller_nip",
                document.id,
                score,
            )
            return None

        # 🔹 1️⃣ znajdź seller
        try:
            seller = self._company_eval.evaluate_from_tax(
                organization_id=document.organization_id,
                actor_user_id=actor_user_id,
                input_tax_number=seller_nip,
                role=CompanyType.SELLER,
                mode=EvaluateMode.NO_CREATE,
                uow=uow,
            )
        except Exception:
            logger.debug(
                "[MATCH] Seller not found | doc=%s | ref=%s | nip=%s | score=%s",
                document.id,
                reference,
                seller_nip,
                score,
            )
            return None

        if not seller:
            logger.debug(
                "[MATCH] Seller missing | doc=%s | ref=%s | nip=%s | score=%s",
                document.id,
                reference,
                seller_nip,
                score,
            )
            return None

        # 🔹 2️⃣ znajdź rekord
        record = uow.financial_records.get_unique_record(
            organization_id=document.organization_id,
            reference=reference,
            seller_id=seller.id,
        )

        if record:
            logger.info(
                "[MATCH] SUCCESS | doc=%s | ref=%s | nip=%s | score=%s | record_id=%s",
                document.id,
                reference,
                seller_nip,
                score,
                record.id,
            )
            
            return record.id

        logger.debug(
            "[MATCH] No record | doc=%s | ref=%s | nip=%s | score=%s",
            document.id,
            reference,
            seller_nip,
            score,
        )

        return None