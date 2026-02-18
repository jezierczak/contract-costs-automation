from dataclasses import dataclass, replace
from uuid import UUID
from enum import Enum

from contract_costs.model.base_entity import BaseEntity


class DocumentType(Enum):
    INVOICE = "invoice"
    PROFORMA = "proforma"
    RECEIPT = "receipt"
    CORRECTION = "correction"
    ADVANCE = "advance"
    SETTLEMENT = "settlement"
    SIMPLIFIED = "simplified"
    CORRECTION_ADVANCE = "correction_advance"
    CORRECTION_SETTLEMENT = "correction_settlement"
    CONTRACT = "contract"
    OTHER = "other"
    UNKNOWN = "unknown"

class DocumentSource(Enum):
    OTHER = "other"
    PDF = "pdf"
    KSEF = "ksef"
    IMAGE = "image"
    EMAIL = "email"

@dataclass(slots=True)
class Document(BaseEntity):
    id: UUID
    financial_record_id: UUID | None

    document_source: DocumentSource | None

    # ekstrakcja z LLM
    document_type: DocumentType | None      # invoice / proforma / receipt
    document_number: str | None
    seller_nip: str | None
    parsed_payload: dict | None

    file_hash: str
    file_path: str
    filename: str
    mime_type: str | None
    size: int | None

    def with_document_type(self, document_type: DocumentType) -> "Document":
        return replace(self, document_type=document_type)

    def with_document_number(self, document_number: str) -> "Document":
        return replace(self, document_number=document_number)

    def with_seller_nip(self, seller_nip: str) -> "Document":
        return replace(self, seller_nip=seller_nip)
