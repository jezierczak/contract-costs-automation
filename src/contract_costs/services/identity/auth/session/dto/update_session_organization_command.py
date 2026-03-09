from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import ActionType, action_type


@dataclass(frozen=True, slots=True)
@action_type(ActionType.SYSTEM)
class UpdateSessionOrganizationCommand(Action):
    session_id: UUID
    organization_id: UUID
