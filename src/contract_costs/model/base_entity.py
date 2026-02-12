from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(slots=True)
class BaseEntity:
    id: UUID
    organization_id: UUID

    created_at: datetime
    created_by_user_id: UUID | None

    updated_at: datetime | None
    updated_by_user_id: UUID | None
