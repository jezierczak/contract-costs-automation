from dataclasses import dataclass

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.query import Query


@dataclass(slots=True, frozen=True)
@action_type(ActionType.FINANCIAL_RECORD_MANAGEMENT)
class RecordMainboardStatsQuery(Query):
    ...