from dataclasses import dataclass
from uuid import UUID
from datetime import date
from decimal import Decimal

@dataclass
class CostProgressSnapshot:
    id: UUID
    contract_id: UUID
    cost_node_id: UUID | None   # None = cały kontrakt
    snapshot_date: date

    planned_amount: Decimal
    executed_amount: Decimal
    progress_percent: Decimal