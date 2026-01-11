from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CostNodePrepareDTO:
    code: str
    name: str
    parent_code: str | None
    budget: Decimal | None
    quantity: Decimal | None
    unit: str | None
    is_active: bool
