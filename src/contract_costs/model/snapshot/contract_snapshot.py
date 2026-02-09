from dataclasses import dataclass
from uuid import UUID
from datetime import date, datetime

from contract_costs.model.base_entity import BaseEntity


@dataclass(slots=True)
class ContractSnapshot(BaseEntity):
    id: UUID
    contract_id: UUID
    snapshot_date: date          # dzień, do którego liczony jest stan

