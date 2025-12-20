from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.cost_progress_snapshot import CostProgressSnapshot


class CostProgressSnapshotRepository(ABC):
    @abstractmethod
    def add(self, snapshot: CostProgressSnapshot) -> None:
        ...

    @abstractmethod
    def get_by_contract(self, contract_id: UUID) -> list[CostProgressSnapshot]:
        ...

    @abstractmethod
    def get_latest(self, contract_id: UUID, cost_node_id: UUID | None) -> CostProgressSnapshot | None:
        ...