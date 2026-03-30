from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.command import Command
from contract_costs.action_bus.action_type import ActionType, action_type


@dataclass(frozen=True)
@action_type(ActionType.DOCUMENT_MANAGEMENT)
class UnattachDocumentCommand(Command):
    document_id: UUID