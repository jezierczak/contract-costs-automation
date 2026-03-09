from dataclasses import dataclass

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import action_type, ActionType


@dataclass(frozen=True,slots=True)
@action_type(ActionType.SYSTEM)
class AuthenticateUserCommand(Action):
    login: str
    password: str