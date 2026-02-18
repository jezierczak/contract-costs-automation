from dataclasses import dataclass
from datetime import date
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.query import Query


@action_type(ActionType.CONTRACT_VIEW)
@dataclass(frozen=True)
class ContractDetailsQuery(Query):
    contract_id: UUID
    at_date: date | None = None
