from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

@dataclass(frozen=True)
class ContractNodeSnapshotDTO:
    # --- identity / tree ---
    node_id: UUID
    parent_id: UUID | None
    code: str
    name: str
    level: int

    # --- planning / progress ---
    planned_budget: Decimal
    progress: Decimal  # 0–1 (nie %)

    # --- financials ---
    net: Decimal
    vat: Decimal
    gross: Decimal
    non_deductible: Decimal

    revenue: Decimal

    @property
    def progress_percent(self) -> Decimal:
        return (self.progress * Decimal("100")).quantize(Decimal("0.01"))

@dataclass(frozen=True)
class ContractSnapshotDTO:
    snapshot_id: UUID
    contract_code: str
    snapshot_date: date

    nodes: list[ContractNodeSnapshotDTO]
