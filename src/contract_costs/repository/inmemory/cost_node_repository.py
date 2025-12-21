from uuid import UUID
from contract_costs.model.cost_node import CostNode
from contract_costs.repository.cost_node_repository import CostNodeRepository


class InMemoryCostNodeRepository(CostNodeRepository):

    def __init__(self) -> None:
        self._nodes: dict[UUID, CostNode] = {}

    def add(self, cost_node: CostNode) -> None:
        self._nodes[cost_node.id] = cost_node

    def add_all(self, cost_nodes: list[CostNode]) -> None:
        for cost_node in cost_nodes:
            self._nodes[cost_node.id] = cost_node

    def get(self, cost_node_id: UUID) -> CostNode | None:
        return self._nodes.get(cost_node_id)

    def list_nodes(self) -> list[CostNode]:
        return list(self._nodes.values())

    def list_by_parent(self, parent_id: UUID) -> list[CostNode]:
        return [
            node for node in self._nodes.values()
            if node.parent_id == parent_id
        ]

    def list_by_contract(self, contract_id: UUID) -> list[CostNode]:
        return [
            node for node in self._nodes.values()
            if node.contract_id == contract_id
        ]

    def delete_by_contract(self, contract_id: UUID) -> None:
        to_delete = [
            node_id
            for node_id, node in self._nodes.items()
            if node.contract_id == contract_id
        ]

        for node_id in to_delete:
            del self._nodes[node_id]


    def update(self, cost_node: CostNode) -> None:
        self._nodes[cost_node.id] = cost_node

    def exists(self, cost_node_id: UUID) -> bool:
        return cost_node_id in self._nodes

    def has_costs(self, contract_id: UUID) -> bool:
        return any(
            node.contract_id == contract_id
            for node in self._nodes.values()
        )