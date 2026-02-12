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
    has_payload: bool
    has_record: bool
    created_at: datetime
    file_path: str
