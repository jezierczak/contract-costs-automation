from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateValueTypeCommand:
    value_type_id: UUID
    name: str
    description: str | None
