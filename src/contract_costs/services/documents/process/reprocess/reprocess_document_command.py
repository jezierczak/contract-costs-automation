from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.command import Command
from contract_costs.action_bus.action_type import action_type, ActionType


@dataclass(frozen=True)
@action_type(ActionType.UPLOAD_DOCUMENT)
class ReprocessDocumentCommand(Command):
    document_id: UUID
    force: bool
