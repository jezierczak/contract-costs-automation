from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command


@dataclass(frozen=True,slots=True)
@action_type(ActionType.ORG_USER_MANAGEMENT)
class DeactivateOrganizationUserCommand(Command):
    organization_id: UUID
    target_user_id: UUID
    actor_user_id: UUID
