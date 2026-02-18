from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command


@dataclass(frozen=True,slots=True)
@action_type(ActionType.ORG_CONTEXT_SWITCH)
class RemoveOrganizationUserCommand(Command):
    organization_id: UUID
    target_user_id: UUID
    actor_user_id: UUID
