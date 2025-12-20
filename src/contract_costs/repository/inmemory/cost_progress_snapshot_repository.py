from uuid import UUID
from contract_costs.model.cost_progress_snapshot import CostProgressSnapshot
from contract_costs.repository.cost_progress_snapshot_repository import (
    CostProgressSnapshotRepository
)


class InMemoryCostProgressSnapshotRepository(CostProgressSnapshotRepository):

    def __init__(self) -> None:
        self._snapshots: list[CostProgressSnapshot] = []

    def add(self, snapshot: CostProgressSnapshot) -> None:
        self._snapshots.append(snapshot)

    def get_by_contract(self, contract_id: UUID) -> list[CostProgressSnapshot]:
        return [
            s for s in self._snapshots
            if s.contract_id == contract_id
        ]

    def get_latest(
        self,
        contract_id: UUID,
        cost_node_id: UUID | None
    ) -> CostProgressSnapshot | None:
        candidates = [
            s for s in self._snapshots
            if s.contract_id == contract_id
            and s.cost_node_id == cost_node_id
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda s: s.snapshot_date)
