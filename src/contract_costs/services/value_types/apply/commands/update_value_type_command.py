from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.query import Query


@dataclass(frozen=True,slots=True)
@action_type(ActionType.ORGANIZATION_SETTINGS_MANAGEMENT)
class UpdateValueTypeCommand(Query):
    value_type_id: UUID
    name: str
    description: str | None
