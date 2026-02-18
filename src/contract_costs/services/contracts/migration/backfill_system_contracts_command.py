from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import ActionType, action_type


@action_type(ActionType.SYSTEM_CREATE_ORGANIZATION_NEW_USER)
@dataclass(frozen=True, slots=True)
class BackfillSystemContractsCommand(Action):
    organization_id: UUID
    actor_user_id: UUID