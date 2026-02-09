from datetime import date
from uuid import UUID

from contract_costs.model.snapshot.contract_snapshot import ContractSnapshot
from contract_costs.repository.snapshot.contract_snapshot_repository import (
    ContractSnapshotRepository,
)


class InMemoryContractSnapshotRepository(ContractSnapshotRepository):

    def __init__(self) -> None:
        self._snapshots: dict[UUID, ContractSnapshot] = {}

    # =========================
    # CREATE
    # =========================

    def add(self, snapshot: ContractSnapshot) -> None:
        if snapshot.id in self._snapshots:
            raise ValueError(f"Snapshot {snapshot.id} already exists")

        self._snapshots[snapshot.id] = snapshot

    # =========================
    # READ
    # =========================

    def get(
        self,
        *,
        organization_id: UUID,
        snapshot_id: UUID,
    ) -> ContractSnapshot | None:
        snapshot = self._snapshots.get(snapshot_id)
        if snapshot and snapshot.organization_id == organization_id:
            return snapshot
        return None

    def get_by_contract_and_date(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
        snapshot_date: date,
    ) -> ContractSnapshot | None:
        for snapshot in self._snapshots.values():
            if (
                snapshot.organization_id == organization_id
                and snapshot.contract_id == contract_id
                and snapshot.snapshot_date == snapshot_date
            ):
                return snapshot
        return None

    def list_by_contract(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
    ) -> list[ContractSnapshot]:
        return sorted(
            (
                s for s in self._snapshots.values()
                if s.organization_id == organization_id
                and s.contract_id == contract_id
            ),
            key=lambda s: s.snapshot_date,
        )

    # =========================
    # TECHNICAL
    # =========================

    def list_all(
        self,
        *,
        organization_id: UUID,
    ) -> list[ContractSnapshot]:
        return sorted(
            (
                s for s in self._snapshots.values()
                if s.organization_id == organization_id
            ),
            key=lambda s: s.snapshot_date,
        )
