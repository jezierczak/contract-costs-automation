from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ValueTypeDTO:
    id: UUID
    code: str
    name: str
    description: str | None
    direction: str
    is_active: bool
