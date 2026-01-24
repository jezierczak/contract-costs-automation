from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.model.snapshot.contract_node_snapshot import (
    ContractNodeSnapshot,
)


class ContractNodeSnapshotRepository(ABC):

    @abstractmethod
    def add_many(
        self,
        snapshots: list[ContractNodeSnapshot],
    ) -> None:
        ...

    @abstractmethod
    def list_by_snapshot(
        self,
        snapshot_id: UUID,
    ) -> list[ContractNodeSnapshot]:
        ...

    @abstractmethod
    def get(
        self,
        node_snapshot_id: UUID,
    ) -> ContractNodeSnapshot | None:
        ...

    @abstractmethod
    def get_root_by_snapshot(self, snapshot_id: UUID) -> ContractNodeSnapshot | None:
        ...

    # techniczne
    @abstractmethod
    def list_all(self) -> list[ContractNodeSnapshot]: ...