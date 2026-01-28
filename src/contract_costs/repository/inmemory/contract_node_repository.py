from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.contract_node import ContractNode
from contract_costs.repository.contract_node_repository import ContractNodeRepository


class InMemoryContractNodeRepository(ContractNodeRepository):

    def __init__(self) -> None:
        self._nodes: dict[UUID, ContractNode] = {}

    # =========================================================
    # CREATE
    # =========================================================

    def add(self, contract_node: ContractNode) -> None:
        self._nodes[contract_node.id] = contract_node

    def add_all(self, contract_nodes: list[ContractNode]) -> None:
        for node in contract_nodes:
            self.add(node)

    # =========================================================
    # PROGRESS
    # =========================================================

    def add_progress(
        self,
        node_id: UUID,
        progress: Decimal,
        progress_date: date,
    ) -> None:
        node = self._nodes.get(node_id)
        if not node:
            raise KeyError(f"ContractNode {node_id} not found")

        node.progress_history[progress_date] = progress

    # =========================================================
    # READ
    # =========================================================

    def get(self, contract_node_id: UUID) -> ContractNode | None:
        return self._nodes.get(contract_node_id)

    def get_by_code(self, contract_node_code: str) -> ContractNode | None:
        for node in self._nodes.values():
            if node.code == contract_node_code:
                return node
        return None

    def list_nodes(self) -> list[ContractNode]:
        return list(self._nodes.values())

    def list_by_parent(self, parent_id: UUID) -> list[ContractNode]:
        return [
            node for node in self._nodes.values()
            if node.parent_id == parent_id
        ]

    def list_by_contract(self, contract_id: UUID) -> list[ContractNode]:
        return [
            node for node in self._nodes.values()
            if node.contract_id == contract_id
        ]

    def list_leaf_nodes_for_active_contracts(self) -> list[ContractNode]:
        # identyczna semantyka jak SQL:
        # liść = nie występuje jako parent_id
        parent_ids = {
            node.parent_id
            for node in self._nodes.values()
            if node.parent_id is not None
        }

        return [
            node for node in self._nodes.values()
            if node.id not in parent_ids
        ]

    # =========================================================
    # UPDATE / DELETE
    # =========================================================

    def update(self, contract_node: ContractNode) -> None:
        if contract_node.id not in self._nodes:
            raise KeyError(f"ContractNode {contract_node.id} not found")

        self._nodes[contract_node.id] = contract_node

    def update_many(self, contract_nodes: list[ContractNode]) -> None:
        for node in contract_nodes:
            self.update(node)

    def delete_by_contract(self, contract_id: UUID) -> None:
        to_delete = [
            node_id
            for node_id, node in self._nodes.items()
            if node.contract_id == contract_id
        ]

        for node_id in to_delete:
            del self._nodes[node_id]

    def delete_many(self, ids: list[UUID]) -> None:
        for node_id in ids:
            self._nodes.pop(node_id, None)

    # =========================================================
    # CHECKS
    # =========================================================

    def exists(self, contract_node_id: UUID) -> bool:
        return contract_node_id in self._nodes

    def has_values(self, contract_id: UUID) -> bool:
        # identyczna semantyka jak MySQL:
        # czy kontrakt ma JAKIEKOLWIEK node'y
        return any(
            node.contract_id == contract_id
            for node in self._nodes.values()
        )

    def node_has_values(self, contract_node_id: UUID) -> bool:
        raise NotImplementedError(
            "node_has_values requires InvoiceLineRepository (not available in-memory)"
        )
