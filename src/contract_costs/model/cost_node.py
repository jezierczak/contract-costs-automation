from  dataclasses import dataclass
from decimal import Decimal
from typing import TypedDict
from uuid import UUID

from contract_costs.model.unit_of_measure import UnitOfMeasure


class CostNodeInput(TypedDict):
    code: str
    name: str
    budget: Decimal | None
    quantity: Decimal | None
    unit: UnitOfMeasure | None
    children: list["CostNodeInput"]
    is_active: bool


@dataclass
class CostNode:
    id: UUID
    contract_id: UUID
    code: str
    name: str
    parent_id: UUID | None
    quantity: Decimal | None
    unit: UnitOfMeasure | None
    budget: Decimal | None
    is_active: bool
