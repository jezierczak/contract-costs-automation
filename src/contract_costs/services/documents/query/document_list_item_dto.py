from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class DocumentListItemDto:
    document_id: UUID
    file_name: str
    document_source: str
    document_type: str
    document_number: str | None
    seller_nip: str | None
    document_status: str
    financial_record_id: UUID | None
    has_payload: bool
    has_record: bool
    created_at: datetime
    file_path: str
    confidence_score: int | None
    confidence_breakdown:dict | None
