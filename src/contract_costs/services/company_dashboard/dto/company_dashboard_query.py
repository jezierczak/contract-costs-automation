from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.query import Query


@dataclass(slots=True, frozen=True)
@action_type(action=ActionType.VIEW)
class CompanyDashboardQuery(Query):
    organization_id: UUID
    company_id: UUID | None = None
    tax_number: str | None = None
    year: int | None = None