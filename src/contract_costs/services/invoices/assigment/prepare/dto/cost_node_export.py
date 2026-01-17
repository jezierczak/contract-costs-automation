from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal

@dataclass(frozen=True)
class CostNodeExport:
    id: UUID
    contract_id: UUID
    parent_id: UUID | None

    contract_code: str
    code: str
    name: str
    budget: Decimal | None

