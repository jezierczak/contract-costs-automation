from decimal import Decimal
from uuid import UUID
import logging
import re
from enum import Enum

from contract_costs.model.amount import Amount
from contract_costs.model.company import CompanyType
from contract_costs.model.document import Document
from contract_costs.services.companies.company_evaluate_orchestrator import (
    EvaluateMode,
    CompanyEvaluateOrchestrator,
)
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import (
    DocumentParseNormalizer,
)
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import (
    DocumentParseResult,
)
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)


class MatchMode(str, Enum):
    STRICT = "strict"
    CANDIDATE = "candidate"


class FindMatchingRecordService:

    def __init__(
        self,
        company_evaluator: CompanyEvaluateOrchestrator,
        document_parse_normalizer: DocumentParseNormalizer,
    ):
        self._company_eval = company_evaluator
        self._normalizer = document_parse_normalizer

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

        # 🔹 seller resolve
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
        # 1️⃣ STRICT
        # =================================
        strict_matches = self._match_by_reference(
            document=document,
            seller_id=seller.id,
            reference=reference,
            uow=uow,
        )

        if strict_matches:
            logger.info(
                "[MATCH][STRICT] SUCCESS | doc=%s | ref=%s | matches=%s",
                document.id,
                reference,
                strict_matches,
            )
            return strict_matches

        if mode == MatchMode.STRICT:
            return []

        # =================================
        # 2️⃣ CANDIDATE
        # =================================
        if not document.parsed_payload:
            logger.debug("[MATCH] No parsed payload | doc=%s", document.id)
            return []

        try:
            parse_result: DocumentParseResult = self._normalizer.normalize_payload(
                document.parsed_payload
            )
        except Exception:
            logger.warning(
                "[MATCH] Normalization failed | doc=%s",
                document.id,
                exc_info=True,
            )
            return []

        candidates = set()

        # 🔹 names
        candidates.update(
            self._match_by_product_names(
                document=document,
                parse_result=parse_result,
                seller_id=seller.id,
                uow=uow,
            )
        )

        # 🔹 lines (gross only)
        candidates.update(
            self._match_by_lines(
                document=document,
                parse_result=parse_result,
                seller_id=seller.id,
                uow=uow,
            )
        )

        # 🔹 total
        candidates.update(
            self._match_by_total(
                document=document,
                parse_result=parse_result,
                seller_id=seller.id,
                uow=uow,
            )
        )

        candidate_matches = list(candidates)

        logger.debug(
            "[MATCH][CANDIDATE] doc=%s | count=%s | candidates=%s",
            document.id,
            len(candidate_matches),
            candidate_matches,
        )

        return candidate_matches

    # =================================
    # STRICT
    # =================================

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

        return [record.id] if record else []

    # =================================
    # NORMALIZATION
    # =================================

    @staticmethod
    def _normalize_name(name: str) -> str:
        name = name.lower()
        name = re.sub(r"\s+", " ", name)
        return name.strip()

    # =================================
    # NAMES
    # =================================

    def _match_by_product_names(
        self,
        *,
        document: Document,
        parse_result: DocumentParseResult,
        seller_id: UUID,
        uow: UnitOfWork,
    ) -> list[UUID]:

        names = sorted(
            self._normalize_name(l.item_name)
            for l in parse_result.lines
            if l.item_name
        )

        if not names:
            return []

        return uow.financial_record_lines.find_financial_record_ids_by_names(
            organization_id=document.organization_id,
            names=names,
            expected=len(names),
            seller_id=seller_id,  # 🔥 ważne
        )

    # =================================
    # LINES (GROSS ONLY)
    # =================================

    @staticmethod
    def _extract_line_amounts(parse_result: DocumentParseResult) -> list[Decimal]:
        return [
            line.amount.gross
            for line in parse_result.lines
            if line.amount
        ]

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

        db_quantities = sorted(
            l.quantity for l in db_lines if l.quantity is not None
        )
        parsed_quantities = sorted(
            l.quantity for l in parse_result.lines if l.quantity is not None
        )

        return db_quantities == parsed_quantities

    def _match_by_lines(
        self,
        *,
        document: Document,
        parse_result: DocumentParseResult,
        seller_id: UUID,
        uow: UnitOfWork,
    ) -> list[UUID]:

        line_amounts = self._extract_line_amounts(parse_result)

        if not line_amounts:
            return []

        expected = len(parse_result.lines)

        record_ids = uow.financial_record_lines.find_financial_record_ids_by_line_amounts(
            organization_id=document.organization_id,
            line_amounts=line_amounts,
            expected=expected,
            tolerance=Decimal("0.01"),
            seller_id=seller_id,  # 🔥 ważne
        )

        if len(record_ids) == 1:
            if not self._validate_line_quantities(
                record_id=record_ids[0],
                parse_result=parse_result,
                document=document,
                uow=uow,
            ):
                return []

        return record_ids

    # =================================
    # TOTAL
    # =================================

    @staticmethod
    def _match_by_total(
        *,
        document: Document,
        parse_result: DocumentParseResult,
        seller_id: UUID,
        uow: UnitOfWork,
    ) -> list[UUID]:

        if not parse_result.lines:
            return []

        summary = Amount.sum([line.amount for line in parse_result.lines])
        total_gross = summary.gross

        return uow.financial_records.find_by_total(
            organization_id=document.organization_id,
            total=total_gross,
            tolerance=Decimal("0.01"),
            seller_id=seller_id,  # 🔥 ważne
        )