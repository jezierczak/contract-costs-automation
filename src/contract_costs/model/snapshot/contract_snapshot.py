from dataclasses import dataclass
from uuid import UUID
from datetime import date, datetime

from contract_costs.model.base_entity import BaseEntity


@dataclass(slots=True , frozen=True)
class ContractSnapshot:
    id: UUID
    organization_id: UUID

    created_at: datetime
    created_by_user_id: UUID | None

    contract_id: UUID
    snapshot_date: date          # dzień, do którego liczony jest stan

