from datetime import date
from uuid import UUID

from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot
from contract_costs.repository.snapshot.contract_snapshot_repository import (
    ContractSnapshotRepository,
)


class InMemoryContractSnapshotRepository(ContractSnapshotRepository):

    def __init__(self) -> None:
        self._snapshots: dict[UUID, ContractSnapshot] = {}

    def add(self, snapshot: ContractSnapshot) -> None:
        if snapshot.id in self._snapshots:
            raise ValueError(f"Snapshot {snapshot.id} already exists")

        self._snapshots[snapshot.id] = snapshot

    def get(self, snapshot_id: UUID) -> ContractSnapshot | None:
        return self._snapshots.get(snapshot_id)

    # def find_by_id_prefix(self, prefix: str) -> list[ContractSnapshot]:
    #     return [snap for snap in self.list_all() if str(snap.id).startswith(prefix)]

    def get_by_contract_and_date(
        self,
        *,
        contract_id: UUID,
        snapshot_date: date,
    ) -> ContractSnapshot | None:
        for snapshot in self._snapshots.values():
            if (
                snapshot.contract_id == contract_id
                and snapshot.snapshot_date == snapshot_date
            ):
                return snapshot
        return None

    def list_by_contract(
        self,
        contract_id: UUID,
    ) -> list[ContractSnapshot]:
        return sorted(
            (
                s for s in self._snapshots.values()
                if s.contract_id == contract_id
            ),
            key=lambda s: s.snapshot_date,
        )

    def list_all(self) -> list[ContractSnapshot]:
        return sorted(
            self._snapshots.values(),
            key=lambda s: s.snapshot_date,
        )

