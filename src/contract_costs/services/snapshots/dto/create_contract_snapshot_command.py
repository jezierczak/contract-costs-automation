from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateContractSnapshotCommand:
    organization_id: UUID
    actor_user_id: UUID | None
    contract_id: UUID
    snapshot_date: date
