from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.command import Command

@dataclass(frozen=True,slots=True)
class ContractNodeProgressUpdate:
    contract_node_id: UUID
    progress: Decimal  # 0–1
    progress_date: date

@action_type(ActionType.CONTRACT_PROGRESS_MANAGEMENT)
@dataclass(frozen=True,slots=True)
class ApplyContractProgressCommand(Command):
    organization_id: UUID
    actor_user_id: UUID
    contract_id: UUID

    updates: list[ContractNodeProgressUpdate]

