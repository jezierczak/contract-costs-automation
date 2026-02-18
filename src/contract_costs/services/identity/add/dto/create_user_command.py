from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command


@dataclass(frozen=True)
@action_type(ActionType.ORG_USER_MANAGEMENT)
class CreateUserCommand(Command):
    login: str
    email: str | None
    full_name: str | None
    # created_by_user_id: UUID | None

