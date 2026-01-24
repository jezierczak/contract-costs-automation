from uuid import UUID

from contract_costs.model.snapshot.contract_node_value_snapshot import (
    ContractNodeValueSnapshot,
)
from contract_costs.repository.snapshot.contract_node_value_snapshot_repository import (
    ContractNodeValueSnapshotRepository,
)


class InMemoryContractNodeValueSnapshotRepository(
    ContractNodeValueSnapshotRepository
):

    def __init__(self) -> None:
        self._values: dict[UUID, ContractNodeValueSnapshot] = {}

    def add_many(
        self,
        values: list[ContractNodeValueSnapshot],
    ) -> None:
        for value in values:
            if value.id in self._values:
                raise ValueError(
                    f"Value snapshot {value.id} already exists"
                )
            self._values[value.id] = value

    def list_by_node_snapshot(
        self,
        node_snapshot_id: UUID,
    ) -> list[ContractNodeValueSnapshot]:
        return [
            v
            for v in self._values.values()
            if v.node_snapshot_id == node_snapshot_id
        ]

    def list_by_snapshot(
        self,
        snapshot_id: UUID,
    ) -> list[ContractNodeValueSnapshot]:
        return [
            v
            for v in self._values.values()
            if v.node_snapshot_id == snapshot_id
            # UWAGA:
            # to zakłada, że node_snapshot_id == snapshot_id
            # w realnym repo SQL będzie JOIN
        ]

    def list_all(
        self,
    ) -> list[ContractNodeValueSnapshot]:
        return list(self._values.values())


