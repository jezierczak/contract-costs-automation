from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from contract_costs.model.base_entity import BaseEntity


@dataclass(slots=True)
class ContractNodeProgress(BaseEntity):
    id: UUID
    contract_node_id: UUID
    progress_date: date
    progress: Decimal  # 0.0000 – 1.0000

