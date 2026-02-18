from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command
from contract_costs.model.value_direction import ValueDirection


@dataclass(frozen=True,slots=True)
@action_type(ActionType.ORGANIZATION_SETTINGS_MANAGEMENT)
class CreateValueTypeCommand(Command):
    code: str
    name: str
    description: str | None
    direction: ValueDirection
    is_active: bool = True
