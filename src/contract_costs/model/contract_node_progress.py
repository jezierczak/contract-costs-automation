from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class ContractNodeProgress:
    id: UUID
    contract_node_id: UUID
    progress_date: date
    progress: Decimal  # 0.0000 – 1.0000
    created_at: datetime
