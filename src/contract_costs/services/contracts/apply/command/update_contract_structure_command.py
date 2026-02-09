from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from contract_costs.model.contract import ContractStatus
from contract_costs.model.contract_node import ContractNodeInput


@dataclass(frozen=True)
class UpdateContractStructureCommand:
    organization_id: UUID
    actor_user_id: UUID
    contract_id: UUID

    name: str
    description: str | None
    start_date: date | None
    end_date: date | None
    budget: Decimal | None
    status: ContractStatus
    path: Path | None

    contract_node_input: list[ContractNodeInput]
