from dataclasses import dataclass
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command
from contract_costs.model.contract import ContractStatus

@dataclass(frozen=True,slots=True)
@action_type(ActionType.CONTRACT_MANAGEMENT)
class SetContractStatusCommand(Command):
    contract_id: UUID
    new_status: ContractStatus
