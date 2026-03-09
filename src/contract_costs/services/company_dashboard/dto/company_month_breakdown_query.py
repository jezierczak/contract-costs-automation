from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.query import Query


@dataclass(slots=True, frozen=True)
@action_type(action=ActionType.VIEW)
class CompanyBreakdownQuery(Query):

    organization_id: UUID
    actor_user_id: UUID

    company_id: UUID
    year: int
    month: int | None