from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.contract_node import ContractNode


class ContractNodeRepository(ABC):

    @abstractmethod
    def add(self, contract_node: ContractNode) -> None:
        """Persist new contract node"""
        ...


    @abstractmethod
    def add_all(self, contract_nodes: list[ContractNode]) -> None:
        """Add new contract nodes group"""
        ...


    @abstractmethod
    def get(self, contract_node_id: UUID) -> ContractNode | None:
        """Get contract node by id"""
        ...

    @abstractmethod
    def get_by_code(self, contract_node_code: str) -> ContractNode | None:
        """Get contract node by code"""
        ...

    @abstractmethod
    def list_nodes(self) -> list[ContractNode]:
        """List all contract nodes"""
        ...
    @abstractmethod
    def list_leaf_nodes_for_active_contracts(self) -> list[ContractNode]:
        ...

    @abstractmethod
    def list_by_parent(self, parent_id: UUID) -> list[ContractNode]:
        """List all contract nodes with parent id"""
        ...

    @abstractmethod
    def list_by_contract(self, contract_id: UUID) -> list[ContractNode]:
        """List all contract nodes with contract id"""
        ...

    @abstractmethod
    def update(self, contract_node: ContractNode) -> None:
        """Update existing contract node"""
        ...
    @abstractmethod
    def update_many(self, nodes: list[ContractNode]) -> None:
        ...

    @abstractmethod
    def delete_by_contract(self, contract_id: UUID) -> None:
        ...

    @abstractmethod
    def delete_many(self, ids: list[UUID]) -> None:
        ...

    @abstractmethod
    def exists(self, contract_node_id: UUID) -> bool:
        """Check if contract node exists"""
        ...

    @abstractmethod
    def has_values(self, contract_id: UUID) -> bool:
        """Check if contract has any nodes"""
        ...

    @abstractmethod
    def node_has_values(self, contract_node_id: UUID) -> bool:
        """Check if any values are assigned to this node"""
        ...