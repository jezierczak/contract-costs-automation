from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import (
    ActionType,
    action_type,
)
from contract_costs.action_bus.command import Command


@action_type(ActionType.SYSTEM)
@dataclass(frozen=True)
class LogBusinessEventCommand(Command):

    level: str
    message: str

    entity_type: str | None = None
    entity_id: UUID | None = None