from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ChangeCostTypeCodeCommand:
    cost_type_id: UUID
    new_code: str
