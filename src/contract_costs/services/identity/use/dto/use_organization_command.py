from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command


@dataclass(frozen=True,slots=True)
@action_type(ActionType.SYSTEM)
class UseOrganizationCommand(Action):
    actor_user_id: UUID
    organization_code: str
