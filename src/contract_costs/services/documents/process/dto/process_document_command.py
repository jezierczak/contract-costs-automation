from dataclasses import dataclass
from uuid import UUID
from contract_costs.action_bus.command import Command
from contract_costs.action_bus.action_type import ActionType, action_type


@action_type(ActionType.UPLOAD_DOCUMENT)
@dataclass(frozen=True)
class ProcessDocumentCommand(Command):
    document_id: UUID
    force: bool=False

