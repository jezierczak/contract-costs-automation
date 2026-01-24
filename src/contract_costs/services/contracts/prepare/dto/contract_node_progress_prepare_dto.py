from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class ContractNodeProgressPrepareDTO:
    contract_code: str
    contract_node_id: UUID
    code: str
    name: str
    budget: Decimal | None
    current_progress_percent: Decimal | None
    new_progress_percent: Decimal | None
    is_active: bool
