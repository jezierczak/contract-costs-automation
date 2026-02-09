from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateValueTypeCommand:
    organization_id: UUID
    actor_user_id: UUID
    value_type_id: UUID
    name: str
    description: str | None
