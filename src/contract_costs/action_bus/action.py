from abc import ABC
from uuid import UUID
from dataclasses import dataclass

from contract_costs.action_bus.action_type import ActionType


@dataclass(frozen=True)
class Action(ABC):
    organization_id: UUID
    actor_user_id: UUID


    @property
    def action_type(self) -> ActionType:
        action = getattr(type(self), "__action_type__", None)
        if action is None:
            raise RuntimeError(
                f"{type(self).__name__} missing @action_type decorator"
            )
        return action