from uuid import UUID

from contract_costs.model.snapshot.contract_node_snapshot import (
    ContractNodeSnapshot,
)
from contract_costs.repository.snapshot.contract_node_snapshot_repository import (
    ContractNodeSnapshotRepository,
)


class InMemoryContractNodeSnapshotRepository(
    ContractNodeSnapshotRepository
):

    def __init__(self) -> None:
        self._snapshots: dict[UUID, ContractNodeSnapshot] = {}

    def add_many(
        self,
        snapshots: list[ContractNodeSnapshot],
    ) -> None:
        for snapshot in snapshots:
            if snapshot.id in self._snapshots:
                raise ValueError(
                    f"Node snapshot {snapshot.id} already exists"
                )
            self._snapshots[snapshot.id] = snapshot

    def get(
        self,
        node_snapshot_id: UUID,
    ) -> ContractNodeSnapshot | None:
        return self._snapshots.get(node_snapshot_id)

    def list_by_snapshot(
        self,
        snapshot_id: UUID,
    ) -> list[ContractNodeSnapshot]:
        return [
            s
            for s in self._snapshots.values()
            if s.snapshot_id == snapshot_id
        ]

    def get_root_by_snapshot(
            self,
            snapshot_id: UUID,
    ) -> ContractNodeSnapshot | None:
        raise NotImplementedError(
            "get_root_by_snapshot is not supported for InMemory repository"
        )

    def list_all(
            self,
    ) -> list[ContractNodeSnapshot]:
        return list(self._snapshots.values())

