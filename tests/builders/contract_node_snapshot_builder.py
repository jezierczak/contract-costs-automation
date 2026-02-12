from decimal import Decimal
from uuid import UUID
from contract_costs.common.ids import new_uuid
from contract_costs.model.snapshot.contract_node_snapshot import (
    ContractNodeSnapshot,
)


class ContractNodeSnapshotBuilder:
    def __init__(self):
        self._id = new_uuid()
        self._snapshot_id = new_uuid()
        self._contract_node_id = new_uuid()
        self._planned_budget = Decimal("1000.00")
        self._progress = Decimal("0.5")

    def build(self) -> ContractNodeSnapshot:
        return ContractNodeSnapshot(
            id=self._id,
            snapshot_id=self._snapshot_id,
            contract_node_id=self._contract_node_id,
            planned_budget=self._planned_budget,
            progress=self._progress,
        )

    def with_snapshot_id(self, snapshot_id: UUID):
        self._snapshot_id = snapshot_id
        return self
