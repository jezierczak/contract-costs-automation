from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal

from contract_costs.model.value_direction import ValueDirection


@dataclass(frozen=True)
class ContractNodeValueSnapshot:
    id: UUID
    node_snapshot_id: UUID
    value_type_id: UUID
    net: Decimal
    vat: Decimal
    gross: Decimal
    non_deductible: Decimal
