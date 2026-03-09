from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from contract_costs.services.contracts.query.contract_details.contract_node_value_type_breakdown_dto import \
    ContractNodeValueTypeBreakdownDTO


@dataclass
class ContractNodeDetailsDTO:
    node_id: UUID
    parent_id: UUID | None

    code: str
    name: str
    is_active: bool
    is_leaf: bool
    level: int

    planned_budget: Decimal
    progress: Decimal | None

    net: Decimal              # koszty
    revenue: Decimal          # przychody
    non_deductible: Decimal
    revenue_non_deductible: Decimal
    value_type_breakdown: list[dict[str,str]]

