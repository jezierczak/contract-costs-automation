from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ChangeValueTypeCodeCommand:
    organization_id: UUID
    actor_user_id: UUID
    value_type_id: UUID
    new_code: str
