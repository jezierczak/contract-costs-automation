from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command


@action_type(ActionType.CONTRACT_MANAGEMENT)
@dataclass(frozen=True,slots=True)
class RenameContractNodeCommand(Command):
    contract_id: UUID
    node_id: UUID
    name: str