from dataclasses import replace
from decimal import Decimal
from uuid import UUID

from contract_costs.model.cost_node import CostNode, CostNodeInput
from contract_costs.repository.cost_node_repository import CostNodeRepository


class ContractCostNodeService:

    def __init__(self, cost_node_repository: CostNodeRepository) -> None:
        self._cost_node_repository = cost_node_repository

    def add_node(self, contract_id: UUID, node: CostNode) -> None:
        if node.contract_id != contract_id:
            raise ValueError("Cost node does not belong to given contract")

        if self._cost_node_repository.exists(node.id):
            raise ValueError("Cost node already exists")

        if node.parent_id is not None:
            parent = self._get_node(node.parent_id)
            if parent.contract_id != contract_id:
                raise ValueError("Parent node belongs to different contract")

        self._cost_node_repository.add(node)

    def add_children(
        self,
        contract_id: UUID,
        parent_id: UUID,
        children: list[CostNode],
    ) -> None:
        parent = self._get_node(parent_id)
        if parent.contract_id != contract_id:
            raise ValueError("Parent node belongs to different contract")

        for child in children:
            if child.contract_id != contract_id:
                raise ValueError("Child node belongs to different contract")
            if child.parent_id != parent_id:
                raise ValueError("Child node has invalid parent_id")
            self._cost_node_repository.add(child)

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
        self._cost_node_repository.update(updated)

    def update_budget(
        self,
        contract_id: UUID,
        node_id: UUID,
        budget: Decimal | None,
    ) -> None:
        node = self._get_node(node_id)
        self._assert_contract(contract_id, node)

        updated = replace(node, budget=budget)
        self._cost_node_repository.update(updated)

    def disable_node(self, contract_id: UUID, node_id: UUID) -> None:
        node = self._get_node(node_id)
        self._assert_contract(contract_id, node)

        updated = replace(node, is_active=False)
        self._cost_node_repository.update(updated)

    def _get_node(self, node_id: UUID) -> CostNode:
        node = self._cost_node_repository.get(node_id)
        if node is None:
            raise ValueError("Cost node does not exist")
        return node

    @staticmethod
    def _assert_contract(contract_id: UUID, node: CostNode) -> None:
        if node.contract_id != contract_id:
            raise ValueError("Cost node does not belong to given contract")
