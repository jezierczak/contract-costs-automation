from dataclasses import dataclass
from datetime import date
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.query import Query


@dataclass(slots=True, frozen=True)
@action_type(action=ActionType.VIEW)
class DashboardQuery(Query):
    organization_id: UUID
    today: date | None = None
