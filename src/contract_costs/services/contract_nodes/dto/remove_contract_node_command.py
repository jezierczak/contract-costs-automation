from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command


@action_type(ActionType.CONTRACT_MANAGEMENT)
@dataclass(frozen=True,slots=True)
class RemoveContractNodeCommand(Command):
    contract_id: UUID
    node_id: UUID