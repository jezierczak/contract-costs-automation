from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.model.snapshot.contract_node_value_snapshot import (
    ContractNodeValueSnapshot,
)


class ContractNodeValueSnapshotRepository(ABC):

    @abstractmethod
    def add_many(
        self,
        values: list[ContractNodeValueSnapshot],
    ) -> None:
        ...

    @abstractmethod
    def list_by_node_snapshot(
        self,
        node_snapshot_id: UUID,
    ) -> list[ContractNodeValueSnapshot]:
        ...

    @abstractmethod
    def list_by_snapshot(
        self,
        snapshot_id: UUID,
    ) -> list[ContractNodeValueSnapshot]:
        ...

    # techniczne
    @abstractmethod
    def list_all(self) -> list[ContractNodeValueSnapshot]: ...