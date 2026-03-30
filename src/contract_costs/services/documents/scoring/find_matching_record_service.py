from collections import defaultdict
from decimal import Decimal
from uuid import UUID

from contract_costs.model.amount import AmountInputType
from contract_costs.model.company import CompanyType
from contract_costs.model.document import Document
from contract_costs.services.companies.company_evaluate_orchestrator import EvaluateMode, CompanyEvaluateOrchestrator
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import \
    DocumentParseNormalizer
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import \
    DocumentParseResult
from contract_costs.unit_of_work import UnitOfWork
import logging

logger = logging.getLogger(__name__)


from enum import Enum

class MatchMode(str, Enum):
    STRICT = "strict"
    CANDIDATE = "candidate"

class FindMatchingRecordService:

    def __init__(self, company_evaluator: CompanyEvaluateOrchestrator,document_parse_normalizer: DocumentParseNormalizer):
        self._company_eval = company_evaluator
        self._normalizer=document_parse_normalizer

    def find(
            self,
            *,
            document: Document,
            actor_user_id: UUID,
            uow: UnitOfWork,
            mode: MatchMode = MatchMode.STRICT,
    ) -> list[UUID]:

        reference = document.document_number
        seller_nip = document.seller_nip
        score = document.scoring.score if document.scoring else None

        if not reference or not seller_nip:
            logger.debug(
                "[MATCH] Skipped | doc=%s | score=%s | missing reference or seller_nip",
                document.id,
                score,
            )
            return []

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
            return []

        if not seller:
            logger.debug(
                "[MATCH] Seller missing | doc=%s | ref=%s | nip=%s | score=%s",
                document.id,
                reference,
                seller_nip,
                score,
            )
            return []

        # =================================
        # 1️⃣ STRICT MATCH
        # =================================
        strict_matches = self._match_by_reference(
            document=document,
            seller_id=seller.id,
            reference=reference,
            uow=uow,
        )

        if strict_matches:
            logger.info(
                "[MATCH][STRICT] SUCCESS | doc=%s | ref=%s | nip=%s | matches=%s",
                document.id,
                reference,
                seller_nip,
                strict_matches,
            )
            return strict_matches

        # =================================
        # STRICT MODE → STOP
        # =================================
        if mode == MatchMode.STRICT:
            return []

        # =================================
        # 2️⃣ CANDIDATE MATCH
        # =================================
        parse_result: DocumentParseResult = self._normalizer.normalize_payload(
            document.parsed_payload
        )

        candidate_matches = self._match_by_lines(
            document=document,
            parse_result=parse_result,
            uow=uow,
        )

        if candidate_matches:
            logger.info(
                "[MATCH][CANDIDATE] SUCCESS | doc=%s | ref=%s | nip=%s | matches=%s",
                document.id,
                reference,
                seller_nip,
                candidate_matches,
            )
            return candidate_matches

        logger.debug(
            "[MATCH] No record | doc=%s | ref=%s | nip=%s | score=%s",
            document.id,
            reference,
            seller_nip,
            score,
        )

        return []

    @staticmethod
    def _match_by_reference(
            *,
            document: Document,
            seller_id: UUID,
            reference: str | None,
            uow: UnitOfWork,
    ) -> list[UUID]:

        if not reference:
            return []

        record = uow.financial_records.get_unique_record(
            organization_id=document.organization_id,
            reference=reference,
            seller_id=seller_id,
        )

        if record:
            return [record.id]

        return []

    @staticmethod
    def _extract_line_amounts(
            parse_result: DocumentParseResult
    ) -> list[Decimal]:

        amounts: list[Decimal] = []

        for line in parse_result.lines:
            amounts.append(line.amount.net)
            amounts.append(line.amount.gross)

        return amounts


    @staticmethod
    def _validate_line_quantities(
            *,
            record_id: UUID,
            parse_result: DocumentParseResult,
            document: Document,
            uow: UnitOfWork,
    ) -> bool:

        db_lines = uow.financial_record_lines.list_by_financial_record_ids(
            organization_id=document.organization_id,
            financial_records_ids=[record_id],
        )

        db_quantities = sorted([l.quantity for l in db_lines])
        parsed_quantities = sorted([l.quantity for l in parse_result.lines])

        return db_quantities == parsed_quantities

    def _match_by_lines(
            self,
            *,
            document: Document,
            parse_result: DocumentParseResult,
            uow: UnitOfWork,
    ) -> list[UUID]:

        line_amounts = self._extract_line_amounts(parse_result)

        if not line_amounts:
            return []

        expected = len(parse_result.lines)

        logger.info("LINE AMOUNTS: %s", expected)

        record_ids = uow.financial_record_lines.find_financial_record_ids_by_line_amounts(
            organization_id=document.organization_id,
            line_amounts=line_amounts,
            expected=expected,
            tolerance=Decimal("0.01"),
        )
        logger.info("MATCHED RECORD IDS: %s", record_ids)

        if len(record_ids) == 1:
            record_id = record_ids[0]

            if not self._validate_line_quantities(
                    record_id=record_id,
                    parse_result=parse_result,
                    document=document,
                    uow=uow,
            ):
                return []

        return record_ids