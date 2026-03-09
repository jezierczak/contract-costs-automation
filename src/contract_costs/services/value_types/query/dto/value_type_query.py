from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.query import Query


@dataclass(frozen=True, slots=True)
@action_type(ActionType.VIEW)
class ValueTypeQuery(Query):
    id: UUID | None = None
    code: str | None = None          # strict
    direction: str | None = None  # "COST" | "REVENUE"
    include_inactive: bool = False
    search: str | None = None        # name + description
