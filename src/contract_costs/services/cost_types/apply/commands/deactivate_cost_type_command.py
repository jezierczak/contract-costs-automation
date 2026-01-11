from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class DeactivateCostTypeCommand:
    cost_type_id: UUID
