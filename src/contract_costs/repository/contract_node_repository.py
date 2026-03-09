from uuid import UUID
from abc import ABC, abstractmethod

from contract_costs.model.contract_node import ContractNode
from contract_costs.model.contract_node_progress import ContractNodeProgress


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
    def get(self,
            *,
            organization_id: UUID,
            contract_node_id: UUID,
    ) -> ContractNode | None:
        """Get contract node by id"""
        ...

    @abstractmethod
    def get_by_code(self,

                    organization_id: UUID,
                    contract_id: UUID,
                    contract_node_code: str) -> ContractNode | None:
        """Get contract node by code"""
        ...

    @abstractmethod
    def list_nodes(self,*,organization_id: UUID) -> list[ContractNode]:
        """List all contract nodes"""
        ...
    @abstractmethod
    def list_leaf_nodes_for_active_contracts(self,*,organization_id: UUID) -> list[ContractNode]:
        ...

    @abstractmethod
    def list_by_parent(self,
                       *,
                       organization_id: UUID,
                       parent_id: UUID) -> list[ContractNode]:
        """List all contract nodes with parent id"""
        ...

    @abstractmethod
    def list_by_contract(self,
                         *,
                         organization_id: UUID,
                         contract_id: UUID) -> list[ContractNode]:
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
    def delete_by_contract(self,
                           *,
                           organization_id: UUID,
                           contract_id: UUID) -> None:
        ...

    @abstractmethod
    def delete_many(self,
                    *,
                    organization_id: UUID,
                    ids: list[UUID]) -> None:
        ...

    @abstractmethod
    def exists(self,
               *,
               organization_id: UUID,
               contract_node_id: UUID) -> bool:
        """Check if contract node exists"""
        ...

    @abstractmethod
    def has_values(self,
                   *,
                   organization_id: UUID,
                   contract_id: UUID) -> bool:
        """Check if contract has any nodes"""
        ...

    @abstractmethod
    def node_has_values(self,
                        *,
                        organization_id: UUID,
                        contract_node_id: UUID) -> bool:
        """Check if any values are assigned to this node"""
        ...

    @abstractmethod
    def list_nodes_with_values(
            self,
            *,
            organization_id: UUID,
            contract_id: UUID,
    ) -> list[UUID]:
        """Return node IDs that have assigned values"""
        ...

    @abstractmethod
    def add_progress(self, progress: ContractNodeProgress) -> None:
        """Add or update progress for contract node"""
        ...

