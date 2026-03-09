from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import action_type, ActionType



@dataclass(frozen=True,slots=True)
@action_type(ActionType.SYSTEM)
class CreateSessionCommand(Action):
    actor_user_id: UUID
    organization_id: UUID | None