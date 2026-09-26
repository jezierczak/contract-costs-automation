from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.query import Query


@dataclass(frozen=True, slots=True)
@action_type(ActionType.VIEW)
class CompanyDetailQuery(Query):
    company_id: UUID
    owner_company_id: UUID | None = None