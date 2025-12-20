from  dataclasses import dataclass
from decimal import Decimal
from typing import TypedDict
from uuid import UUID


class CostNodeInput(TypedDict):
    code: str
    name: str
    budget: Decimal | None
    children: list["CostNodeInput"]


@dataclass
class CostNode:
    id: UUID
    contract_id: UUID
    code: str
    name: str
    parent_id: UUID | None
    budget: Decimal | None
    is_active: bool
