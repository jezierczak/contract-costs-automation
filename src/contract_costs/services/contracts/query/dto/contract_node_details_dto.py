from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

@dataclass
class ContractNodeDetailsDTO:
    node_id: UUID
    parent_id: UUID | None

    code: str
    name: str
    is_active: bool
    is_leaf: bool

    planned_budget: Decimal
    progress: Decimal | None

    net: Decimal              # koszty
    revenue: Decimal          # przychody
    non_deductible: Decimal