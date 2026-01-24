from dataclasses import dataclass
from datetime import date
from uuid import UUID
from decimal import Decimal


@dataclass(frozen=True)
class ContractSnapshotListDTO:
    snapshot_id: UUID
    snapshot_date: date

    contract_id: UUID
    contract_code: str

    planned_budget: Decimal
    progress: Decimal

    net_cost: Decimal
    gross_cost: Decimal
    non_deductible: Decimal
    revenue: Decimal
