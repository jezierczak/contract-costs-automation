from dataclasses import replace
from decimal import Decimal
from uuid import UUID

from contract_costs.model.contract_node import ContractNode, ContractNodeInput
from contract_costs.repository.contract_node_repository import ContractNodeRepository


class ContractContractNodeService:

    def __init__(self, contract_node_repository: ContractNodeRepository) -> None:
        self._contract_node_repository = contract_node_repository

    def add_node(self, contract_id: UUID, node: ContractNode) -> None:
        if node.contract_id != contract_id:
            raise ValueError("Cost node does not belong to given contract")

        if self._contract_node_repository.exists(node.id):
            raise ValueError("Cost node already exists")

        if node.parent_id is not None:
            parent = self._get_node(node.parent_id)
            if parent.contract_id != contract_id:
                raise ValueError("Parent node belongs to different contract")

        self._contract_node_repository.add(node)

    def add_children(
        self,
        contract_id: UUID,
        parent_id: UUID,
        children: list[ContractNode],
    ) -> None:
        parent = self._get_node(parent_id)
        if parent.contract_id != contract_id:
            raise ValueError("Parent node belongs to different contract")

        for child in children:
            if child.contract_id != contract_id:
                raise ValueError("Child node belongs to different contract")
            if child.parent_id != parent_id:
                raise ValueError("Child node has invalid parent_id")
            self._contract_node_repository.add(child)

    def move_node(
        self,
        contract_id: UUID,
        node_id: UUID,
        new_parent_id: UUID | None,
    ) -> None:
        node = self._get_node(node_id)
        self._assert_contract(contract_id, node)

        if new_parent_id is not None:
            parent = self._get_node(new_parent_id)
            self._assert_contract(contract_id, parent)

        updated = replace(node, parent_id=new_parent_id)
        self._contract_node_repository.update(updated)

    def update_budget(
        self,
        contract_id: UUID,
        node_id: UUID,
        budget: Decimal | None,
    ) -> None:
        node = self._get_node(node_id)
        self._assert_contract(contract_id, node)

        updated = replace(node, budget=budget)
        self._contract_node_repository.update(updated)

    def disable_node(self, contract_id: UUID, node_id: UUID) -> None:
        node = self._get_node(node_id)
        self._assert_contract(contract_id, node)

        updated = replace(node, is_active=False)
        self._contract_node_repository.update(updated)

    def _get_node(self, node_id: UUID) -> ContractNode:
        node = self._contract_node_repository.get(node_id)
        if node is None:
            raise ValueError("Cost node does not exist")
        return node

    @staticmethod
    def _assert_contract(contract_id: UUID, node: ContractNode) -> None:
        if node.contract_id != contract_id:
            raise ValueError("Cost node does not belong to given contract")
