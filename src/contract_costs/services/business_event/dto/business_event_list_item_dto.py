from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class BusinessEventListItemDto:
    id: UUID

    level: str
    message: str

    entity_type: str | None
    entity_id: UUID | None

    created_at: datetime