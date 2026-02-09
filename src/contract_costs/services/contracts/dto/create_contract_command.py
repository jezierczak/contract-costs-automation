from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import UUID

from contract_costs.model.company import Company
from contract_costs.model.contract import ContractStatus


@dataclass(frozen=True)
class CreateContractCommand:
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
