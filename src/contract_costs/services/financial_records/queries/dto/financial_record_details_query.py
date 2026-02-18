from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.query import Query


@dataclass(frozen=True, slots=True)
@action_type(ActionType.FINANCIAL_RECORD_VIEW)
class FinancialRecordDetailsQuery(Query):
    record_id: UUID | None = None
    reference: str | None = None