from dataclasses import dataclass
from pathlib import Path
from typing import TypedDict, Self
from uuid import UUID,uuid4
from datetime import date
from decimal import Decimal
from enum import Enum
import contract_costs.config as cfg
from contract_costs.model.base_entity import BaseEntity

from contract_costs.model.company import Company


class ContractStatus(Enum):
    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# class ContractStarter(TypedDict):
#     # 🔐 multitenancy + audit
#     organization_id: UUID
#     actor_user_id: UUID
#
#     # 🧾 istniejące pola
#     name: str
#     code: str
#     contract_owner: Company
#     client: Company | None
#     description: str | None
#
#     start_date: date | None
#     end_date: date | None
#
#     budget: Decimal | None
#     path: Path | None
#     status: ContractStatus

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

    # @classmethod
    # def from_contract_starter(cls, data: "ContractStarter") -> "Contract":
    #     now = datetime.utcnow()
    #
    #     return cls(
    #         # BaseEntity
    #         id=uuid4(),
    #         organization_id=data["organization_id"],
    #         created_at=now,
    #         created_by_user_id=data["actor_user_id"],
    #         updated_at=None,
    #         updated_by_user_id=None,
    #
    #         # Contract
    #         code=data["code"],
    #         name=data["name"],
    #         owner=data["contract_owner"],
    #         client=data["client"],
    #         description=data["description"],
    #         start_date=data["start_date"],
    #         end_date=data["end_date"],
    #         budget=data["budget"],
    #         path=(
    #             data["path"]
    #             if data["path"]
    #             else Contract.contract_path(
    #                 cfg.OWNERS_DIR,
    #                 data["contract_owner"].name,
    #             )
    #         ),
    #         status=data["status"],
    #     )

    @staticmethod
    def contract_path(owner, contract_name: str) -> Path:
        safe_name = contract_name.replace(" ", "_").lower()
        return Path(owner.name) / safe_name


    @property
    def is_active(self) -> bool:
        return self.status == ContractStatus.ACTIVE