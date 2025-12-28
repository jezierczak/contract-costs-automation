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
    def get_by_code(self, cost_node_code: str) -> CostNode | None:
        """Get cost node by code"""
        ...

    @abstractmethod
    def list_nodes(self) -> list[CostNode]:
        """List all cost nodes"""
        ...
    @abstractmethod
    def list_leaf_nodes_for_active_contracts(self) -> list[CostNode]:
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
    def update_many(self, nodes: list[CostNode]) -> None:
        ...

    @abstractmethod
    def delete_by_contract(self, contract_id: UUID) -> None:
        ...

    @abstractmethod
    def delete_many(self, ids: list[UUID]) -> None:
        ...

    @abstractmethod
    def exists(self, cost_node_id: UUID) -> bool:
        """Check if cost node exists"""
        ...

    @abstractmethod
    def has_costs(self, contract_id: UUID) -> bool:
        ...

    @abstractmethod
    def node_has_costs(self, cost_node_id: UUID) -> bool:
        ...