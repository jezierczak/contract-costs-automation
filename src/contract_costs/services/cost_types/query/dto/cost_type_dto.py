from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CostTypeDTO:
    id: UUID
    code: str
    name: str
    description: str | None
    is_active: bool
