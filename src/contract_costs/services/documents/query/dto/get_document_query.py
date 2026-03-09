from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.query import Query


@dataclass(frozen=True,slots=True)
@action_type(ActionType.DOCUMENT_MANAGEMENT)
class GetDocumentQuery(Query):
    document_id: UUID