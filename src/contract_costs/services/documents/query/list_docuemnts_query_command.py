from dataclasses import dataclass
from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.query import Query
from contract_costs.model.document import DocumentStatus


@action_type(ActionType.DOCUMENT_MANAGEMENT)
@dataclass(frozen=True)
class ListDocumentsQueryCommand(Query):
    has_payload: bool | None = None
    has_record: bool | None = None
    source: str | None = None
    status: DocumentStatus | None = None