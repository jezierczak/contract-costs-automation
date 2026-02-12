from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from contract_costs.action_bus.action_type import action_type, ActionType
from contract_costs.action_bus.command import Command
from contract_costs.model.company import Company
from contract_costs.model.contract import ContractStatus, ContractType
from contract_costs.model.contract_node import ContractNodeInput


@action_type(ActionType.CREATE_CONTRACT)
@dataclass(frozen=True)
class CreateContractCommand(Command):
    organization_id: UUID
    actor_user_id: UUID

    code: str
    name: str
    description: str | None

    owner: Company
    client: Company | None

    start_date: date | None
    end_date: date | None
    budget: Decimal | None
    path: Path | None
    status: ContractStatus
    contract_type: ContractType
    contract_node_input: list[ContractNodeInput] | None = None
