from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class BusinessEventLevel(str, Enum):
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    INFO = "INFO"

@dataclass(slots=True, frozen=True)
class BusinessEvent:
    id: UUID
    organization_id: UUID

    type: str           # SUCCESS / ERROR / INFO
    message: str

    entity_type: str | None
    entity_id: UUID | None

    created_at: datetime
    created_by_user_id: UUID | None