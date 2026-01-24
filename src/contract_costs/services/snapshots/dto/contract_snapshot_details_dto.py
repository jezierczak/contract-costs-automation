from dataclasses import dataclass
from datetime import date
from uuid import UUID

from contract_costs.services.snapshots.dto.contract_snapshot_node_dto import ContractSnapshotNodeDTO


@dataclass(frozen=True)
class ContractSnapshotDetailsDTO:
    snapshot_id: UUID
    snapshot_date: date

    contract_code: str

    nodes: list[ContractSnapshotNodeDTO]
