from dataclasses import dataclass
from uuid import UUID

from contract_costs.model.value_direction import ValueDirection


@dataclass(frozen=True)
class CreateValueTypeCommand:
    organization_id: UUID
    actor_user_id: UUID | None

    code: str
    name: str
    description: str | None
    direction: ValueDirection
    is_active: bool = True
