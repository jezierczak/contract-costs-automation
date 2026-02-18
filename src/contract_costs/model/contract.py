from dataclasses import dataclass
from pathlib import Path
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

from contract_costs.model.base_entity import BaseEntity

from contract_costs.model.company import Company

class ContractType(Enum):
    PROJECT = "project"
    SYSTEM = "system"
    AGREEMENT= "agreement"

class ContractStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

@dataclass(slots=True)
class Contract(BaseEntity):
    code: str
    name: str

    owner: Company
    client: Company | None
    description: str | None

    start_date: date | None
    end_date: date | None

    budget: Decimal | None
    path: Path | None
    status: ContractStatus

    contract_type: ContractType
    parent_project_id: UUID | None = None


    @staticmethod
    def contract_path(owner, contract_name: str) -> Path:
        safe_name = contract_name.replace(" ", "_").lower()
        return Path(owner.name) / safe_name


    @property
    def is_active(self) -> bool:
        return self.status == ContractStatus.ACTIVE

    @property
    def is_agreement(self) -> bool:
        return self.contract_type == ContractType.AGREEMENT