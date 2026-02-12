from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import ActionType, action_type


@dataclass(frozen=True)
@action_type(ActionType.DELETE_DOCUMENT)
class DeleteDocumentCommand(Action):
    document_id: UUID
