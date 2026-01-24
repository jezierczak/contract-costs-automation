from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class ContractSnapshotNodeDTO:
    node_id: UUID
    parent_id: UUID | None

    code: str
    name: str

    planned_budget: Decimal
    progress: Decimal

    net_cost: Decimal
    gross_cost: Decimal
    revenue: Decimal
    non_deductible: Decimal

    is_leaf: bool
