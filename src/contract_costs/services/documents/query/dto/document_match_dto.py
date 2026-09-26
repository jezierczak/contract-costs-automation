from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class CompanySummaryDto:
    id: UUID
    name: str
    tax_number: str
    to_verify: bool


@dataclass(frozen=True)
class DocumentPartyDto:
    """Sprzedawca albo nabywca: dane z dokumentu + firma znaleziona po NIP-ie."""
    tax_number: str | None
    name: str | None
    street: str | None
    zip_code: str | None
    city: str | None
    # dokładnie po NIP-ie; None = nieznany kontrahent
    company: CompanySummaryDto | None
    # podobne firmy (nazwa, konto, email, ulica, telefon) – tylko podpowiedzi
    suggestions: list[CompanySummaryDto] = field(default_factory=list)


@dataclass(frozen=True)
class MatchCandidateDto:
    record_id: UUID
    reference: str | None
    status: str
    invoice_date: date | None
    total_gross: Decimal
    seller_name: str | None
    buyer_name: str | None
    # dlaczego rekord pasuje: reference / total / lines / names
    reasons: tuple[str, ...]
    # różnice względem dokumentu
    same_seller: bool
    same_buyer: bool
    total_difference: Decimal | None


@dataclass(frozen=True)
class DocumentMatchDto:
    document_id: UUID
    document_source: str | None
    document_type: str | None
    document_number: str | None
    seller_nip: str | None
    file_path: str
    confidence_score: int | None
    confidence_breakdown: dict | None

    invoice_date: date | None
    total_gross: Decimal | None
    seller: DocumentPartyDto
    buyer: DocumentPartyDto
    candidates: list[MatchCandidateDto]
