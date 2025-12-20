from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.cost_node import CostNode


class CostNodeRepository(ABC):

    @abstractmethod
    def add(self, cost_node: CostNode) -> None:
        """Persist new cost node"""
        ...

    @abstractmethod
    def add_all(self, cost_nodes: list[CostNode]) -> None:
        """Add new cost nodes group"""
        ...


    @abstractmethod
    def get(self, cost_node_id: UUID) -> CostNode | None:
        """Get cost node by id"""
        ...

    @abstractmethod
    def list_nodes(self) -> list[CostNode]:
        """List all cost nodes"""
        ...

    @abstractmethod
    def list_by_parent(self, parent_id: UUID) -> list[CostNode]:
        """List all cost nodes with parent id"""
        ...

    @abstractmethod
    def list_by_contract(self, contract_id: UUID) -> list[CostNode]:
        """List all cost nodes with contract id"""
        ...

    @abstractmethod
    def update(self, cost_node: CostNode) -> None:
        """Update existing cost node"""
        ...

    @abstractmethod
    def exists(self, cost_node_id: UUID) -> bool:
        """Check if cost node exists"""
        ...