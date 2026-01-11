from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class UpdateCostTypeCommand:
    cost_type_id: UUID
    name: str
    description: str | None
