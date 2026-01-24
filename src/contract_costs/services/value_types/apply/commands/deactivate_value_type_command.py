from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeactivateValueTypeCommand:
    value_type_id: UUID
