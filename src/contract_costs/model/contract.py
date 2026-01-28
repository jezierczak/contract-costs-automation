from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, Self
from uuid import UUID,uuid4
from datetime import date
from decimal import Decimal
from enum import Enum
import contract_costs.config as cfg

from contract_costs.model.company import Company


class ContractStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ContractStarter(TypedDict):
    name: str
    code: str
    contract_owner: Company
    client: Company | None
    description: str | None

    start_date: date | None
    end_date: date | None

    budget: Decimal | None
    path: Path | None
    status: ContractStatus

@dataclass
class Contract:
    id: UUID
    code: str
    name: str
    owner: Company
    client: Company | None
    description: str | None

    start_date: date | None
    end_date: date | None

    budget: Decimal | None
    path: Path
    status: ContractStatus

    @classmethod
    def from_contract_starter(cls,data: ContractStarter) -> "Contract":
        return Contract(
            id=uuid4(),
            code=data['code'],
            name=data['name'],
            owner=data['contract_owner'],
            client=data['client'],
            description=data['description'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            budget=data['budget'],
            path=data['path'] if data['path'] else Contract.contract_path(cfg.OWNERS_DIR,data['contract_owner'].name),
            status=data['status']
        )

    @staticmethod
    def contract_path(owner, contract_name: str) -> Path:
        safe_name = contract_name.replace(" ", "_").lower()
        return Path(owner.name) / safe_name


    @property
    def is_active(self) -> bool:
        return self.status == ContractStatus.ACTIVE