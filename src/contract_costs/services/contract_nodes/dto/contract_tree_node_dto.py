from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from contract_costs.model.unit_of_measure import UnitOfMeasure


@dataclass(frozen=True, slots=True)
class ContractTreeNodeDTO:
    node_id: UUID
    parent_id: UUID | None

    code: str
    name: str
    quantity: Decimal | None
    unit: UnitOfMeasure | None
    planned_budget: Decimal | None
    is_active: bool

    depth: int

    is_leaf: bool
    has_values: bool

    can_add_child: bool
    can_remove: bool