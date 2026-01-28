from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class ContractListDTO:
    contract_id: UUID
    code: str
    name: str
    is_active: bool

    planned_budget: Decimal
    progress: Decimal | None

    net: Decimal
    gross: Decimal
    non_deduction: Decimal

    revenue: Decimal
