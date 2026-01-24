from dataclasses import dataclass
from uuid import UUID
from datetime import date, datetime


@dataclass(frozen=True)
class ContractSnapshot:
    id: UUID
    contract_id: UUID
    snapshot_date: date          # dzień, do którego liczony jest stan
    created_at: datetime         # moment wykonania snapshota
