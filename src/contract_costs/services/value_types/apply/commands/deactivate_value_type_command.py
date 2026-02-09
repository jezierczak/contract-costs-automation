from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeactivateValueTypeCommand:
    organization_id: UUID
    actor_user_id: UUID
    value_type_id: UUID
