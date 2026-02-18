from dataclasses import dataclass

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command

@dataclass(frozen=True,slots=True)
@action_type(ActionType.DOCUMENT_PROCESSING)
class PrepareDocumentsCommand(Command):
    ...