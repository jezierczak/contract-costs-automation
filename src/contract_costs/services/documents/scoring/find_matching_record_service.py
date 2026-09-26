from dataclasses import dataclass, field
from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID
import logging
import re
from enum import Enum

from contract_costs.model.amount import Amount
from contract_costs.model.company import Company
from contract_costs.model.document import Document
from contract_costs.model.financial_record import FinancialRecord, FinancialRecordStatus
from contract_costs.services.common.resolve_utils import is_placeholder_identifier, normalize_tax_number
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import (
    DocumentParseNormalizer,
)
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import (
    DocumentParseResult,
)
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

# dopasowanie wyłącznie po kwotach (suma / kwoty pozycji) tylko dla rekordów z datą w tym oknie
TOTAL_MATCH_WINDOW = timedelta(days=60)


class MatchReason(str, Enum):
    REFERENCE = "reference"   # ten sam numer u tego samego sprzedawcy (dopasowanie ścisłe)
    TOTAL = "total"           # ta sama suma brutto
    LINES = "lines"           # te same kwoty pozycji
    NAMES = "names"           # te same nazwy pozycji


AMOUNT_REASONS = frozenset({MatchReason.TOTAL, MatchReason.LINES})

@dataclass(frozen=True, slots=True)
class RecordMatch:
    record: FinancialRecord
    reasons: frozenset[MatchReason]

    @property
    def is_strict(self) -> bool:
        return MatchReason.REFERENCE in self.reasons


@dataclass(frozen=True, slots=True)
class MatchResult:
    # NIP-y z dokumentu i firmy znalezione dokładnie po nich (None = brak w bazie)
    seller_tax_number: str | None = None
    buyer_tax_number: str | None = None
    seller: Company | None = None
    buyer: Company | None = None
    matches: list[RecordMatch] = field(default_factory=list)

    @property
    def strict(self) -> list[RecordMatch]:
        return [m for m in self.matches if m.is_strict]

    @property
    def candidates(self) -> list[RecordMatch]:
        return [m for m in self.matches if not m.is_strict]


class FindMatchingRecordService:
    """
    Szuka rekordów, do których pasuje dokument.

    - ścisłe: numer dokumentu + sprzedawca (dokładny NIP),
    - kandydaci: suma brutto, kwoty pozycji, nazwy pozycji – zawsze u tego samego
      sprzedawcy, a gdy nabywca jest znany – też u tego nabywcy; dopasowanie
      wyłącznie po kwotach tylko w oknie ±60 dni od daty dokumentu.
    Każde dopasowanie niesie powody, żeby użytkownik widział, dlaczego rekord pasuje.
    Niczego nie tworzy ani nie aktualizuje.
    """

    def __init__(self, document_parse_normalizer: DocumentParseNormalizer):
        self._normalizer = document_parse_normalizer

    def find(self, *, document: Document, uow: UnitOfWork) -> MatchResult:
        org_id = document.organization_id
        parse_result = self._parse(document)

        seller_tax = document.seller_nip or (parse_result.seller.tax_number if parse_result else None)
        buyer_tax = parse_result.buyer.tax_number if parse_result else None
        seller = self._resolve_company(uow=uow, organization_id=org_id, tax_number=seller_tax)
        buyer = self._resolve_company(uow=uow, organization_id=org_id, tax_number=buyer_tax)

        result = MatchResult(
            seller_tax_number=seller_tax,
            buyer_tax_number=buyer_tax,
            seller=seller,
            buyer=buyer,
        )
        if seller is None:
            logger.debug("[MATCH] Seller not in database | doc=%s | nip=%s", document.id, seller_tax)
            return result

        reasons: dict[UUID, set[MatchReason]] = {}

        def add(record_ids, reason: MatchReason) -> None:
            for record_id in record_ids:
                reasons.setdefault(record_id, set()).add(reason)

        reference = document.document_number
        if reference:
            record = uow.financial_records.get_unique_record(
                organization_id=org_id, reference=reference, seller_id=seller.id,
            )
            if record:
                add([record.id], MatchReason.REFERENCE)

        if parse_result:
            add(self._match_by_names(org_id=org_id, parse_result=parse_result, seller_id=seller.id, uow=uow),
                MatchReason.NAMES)
            add(self._match_by_lines(org_id=org_id, parse_result=parse_result, seller_id=seller.id, uow=uow),
                MatchReason.LINES)
            add(self._match_by_total(org_id=org_id, parse_result=parse_result, seller_id=seller.id, uow=uow),
                MatchReason.TOTAL)

        invoice_date = parse_result.record.invoice_date if parse_result else None
        matches = []
        for record_id, record_reasons in reasons.items():
            record = uow.financial_records.get(organization_id=org_id, record_id=record_id)
            if record is None or not self._is_candidate(
                record=record, document=document, seller=seller, buyer=buyer,
                strict=MatchReason.REFERENCE in record_reasons,
            ):
                continue
            if record_reasons <= AMOUNT_REASONS and not self._within_window(record.invoice_date, invoice_date):
                continue
            matches.append(RecordMatch(record=record, reasons=frozenset(record_reasons)))

        matches.sort(key=lambda m: (not m.is_strict, -len(m.reasons), m.record.reference or ""))
        logger.debug(
            "[MATCH] doc=%s | matches=%s",
            document.id,
            [(m.record.reference, sorted(r.value for r in m.reasons)) for m in matches],
        )
        return MatchResult(
            seller_tax_number=seller_tax,
            buyer_tax_number=buyer_tax,
            seller=seller,
            buyer=buyer,
            matches=matches,
        )

    # =================================
    # HELPERS
    # =================================

    def _parse(self, document: Document) -> DocumentParseResult | None:
        if not document.parsed_payload:
            return None
        try:
            return self._normalizer.normalize_payload(document.parsed_payload)
        except Exception:
            logger.warning("[MATCH] Normalization failed | doc=%s", document.id, exc_info=True)
            return None

    @staticmethod
    def _resolve_company(*, uow: UnitOfWork, organization_id: UUID, tax_number: str | None) -> Company | None:
        if not tax_number:
            return None
        value = str(tax_number).strip()
        key = value if is_placeholder_identifier(value) else normalize_tax_number(value)
        if not key:
            return None
        return uow.companies.get_by_tax_number(key, organization_id)

    @staticmethod
    def _is_candidate(
        *,
        record: FinancialRecord,
        document: Document,
        seller: Company,
        buyer: Company | None,
        strict: bool,
    ) -> bool:
        if record.status == FinancialRecordStatus.DELETED:
            return False
        if record.id == document.financial_record_id:
            return False
        if record.seller_id != seller.id:
            return False
        # numer + sprzedawca wystarczają; kandydat „po kwotach” musi mieć też tego nabywcę
        if not strict and buyer is not None and record.buyer_id != buyer.id:
            return False
        return True

    @staticmethod
    def _within_window(record_date: date | None, document_date: date | None) -> bool:
        if record_date is None or document_date is None:
            return True
        return abs(record_date - document_date) <= TOTAL_MATCH_WINDOW

    @staticmethod
    def _normalize_name(name: str) -> str:
        name = name.lower()
        name = re.sub(r"\s+", " ", name)
        return name.strip()

    def _match_by_names(
        self, *, org_id: UUID, parse_result: DocumentParseResult, seller_id: UUID, uow: UnitOfWork,
    ) -> list[UUID]:
        names = sorted(
            self._normalize_name(line.item_name)
            for line in parse_result.lines
            if line.item_name
        )
        if not names:
            return []
        return uow.financial_record_lines.find_financial_record_ids_by_names(
            organization_id=org_id,
            names=names,
            expected=len(names),
            seller_id=seller_id,
        )

    @staticmethod
    def _quantities_match(*, org_id: UUID, record_id: UUID, parse_result: DocumentParseResult, uow: UnitOfWork) -> bool:
        db_lines = uow.financial_record_lines.list_by_financial_record_ids(
            organization_id=org_id,
            financial_records_ids=[record_id],
        )
        db_quantities = sorted(l.quantity for l in db_lines if l.quantity is not None)
        parsed_quantities = sorted(l.quantity for l in parse_result.lines if l.quantity is not None)
        return db_quantities == parsed_quantities

    def _match_by_lines(
        self, *, org_id: UUID, parse_result: DocumentParseResult, seller_id: UUID, uow: UnitOfWork,
    ) -> list[UUID]:
        line_amounts = [line.amount.gross for line in parse_result.lines if line.amount]
        if not line_amounts:
            return []

        record_ids = uow.financial_record_lines.find_financial_record_ids_by_line_amounts(
            organization_id=org_id,
            line_amounts=line_amounts,
            expected=len(parse_result.lines),
            tolerance=Decimal("0.01"),
            seller_id=seller_id,
        )
        if len(record_ids) == 1 and not self._quantities_match(
            org_id=org_id, record_id=record_ids[0], parse_result=parse_result, uow=uow,
        ):
            return []
        return record_ids

    @staticmethod
    def _match_by_total(
        *, org_id: UUID, parse_result: DocumentParseResult, seller_id: UUID, uow: UnitOfWork,
    ) -> list[UUID]:
        if not parse_result.lines:
            return []
        total_gross = Amount.sum([line.amount for line in parse_result.lines]).gross
        return uow.financial_records.find_by_total(
            organization_id=org_id,
            total=total_gross,
            tolerance=Decimal("0.01"),
            seller_id=seller_id,
        )
