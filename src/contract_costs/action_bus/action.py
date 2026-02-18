from abc import ABC
from dataclasses import dataclass

from contract_costs.action_bus.action_type import ActionType


@dataclass(frozen=True,slots=True)
class Action(ABC):



    @property
    def action_type(self) -> ActionType:
        action = getattr(type(self), "__action_type__", None)
        if action is None:
            raise RuntimeError(
                f"{type(self).__name__} missing @action_type decorator"
            )
        return action