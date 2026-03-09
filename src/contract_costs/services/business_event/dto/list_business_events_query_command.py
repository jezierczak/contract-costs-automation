from dataclasses import dataclass
from contract_costs.action_bus.query import Query
from contract_costs.action_bus.action_type import (
    action_type,
    ActionType,
)

@action_type(ActionType.SYSTEM)
@dataclass(frozen=True,slots=True)
class ListBusinessEventsQueryCommand(Query):

    limit: int = 30