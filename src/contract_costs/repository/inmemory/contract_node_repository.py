from uuid import UUID

from contract_costs.model.contract_node import ContractNode
from contract_costs.model.contract_node_progress import ContractNodeProgress
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

    def add_progress(self, progress: ContractNodeProgress) -> None:
        node = self._nodes.get(progress.contract_node_id)
        if not node:
            raise KeyError(f"ContractNode {progress.contract_node_id} not found")

        if node.organization_id != progress.organization_id:
            raise PermissionError("Cross-organization progress write")

        node.progress_history[progress.progress_date] = progress.progress

    # =========================================================
    # READ
    # =========================================================

    def get(
        self,
        *,
        organization_id: UUID,
        contract_node_id: UUID,
    ) -> ContractNode | None:
        node = self._nodes.get(contract_node_id)
        if not node or node.organization_id != organization_id:
            return None
        return node

    def get_by_code(
        self,
        organization_id: UUID,
        contract_node_code: str,
    ) -> ContractNode | None:
        for node in self._nodes.values():
            if (
                node.organization_id == organization_id
                and node.code == contract_node_code
            ):
                return node
        return None

    def list_nodes(
        self,
        *,
        organization_id: UUID,
    ) -> list[ContractNode]:
        return [
            node
            for node in self._nodes.values()
            if node.organization_id == organization_id
        ]

    def list_by_parent(
        self,
        *,
        organization_id: UUID,
        parent_id: UUID,
    ) -> list[ContractNode]:
        return [
            node
            for node in self._nodes.values()
            if node.organization_id == organization_id
            and node.parent_id == parent_id
        ]

    def list_by_contract(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
    ) -> list[ContractNode]:
        return [
            node
            for node in self._nodes.values()
            if node.organization_id == organization_id
            and node.contract_id == contract_id
        ]

    def list_leaf_nodes_for_active_contracts(
        self,
        *,
        organization_id: UUID,
    ) -> list[ContractNode]:
        nodes = [
            node
            for node in self._nodes.values()
            if node.organization_id == organization_id
        ]

        parent_ids = {
            node.parent_id
            for node in nodes
            if node.parent_id is not None
        }

        return [
            node
            for node in nodes
            if node.id not in parent_ids
        ]

    # =========================================================
    # UPDATE / DELETE
    # =========================================================

    def update(self, contract_node: ContractNode) -> None:
        if contract_node.id not in self._nodes:
            raise KeyError(f"ContractNode {contract_node.id} not found")

        self._nodes[contract_node.id] = contract_node

    def update_many(self, nodes: list[ContractNode]) -> None:
        for node in nodes:
            self.update(node)

    def delete_by_contract(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
    ) -> None:
        to_delete = [
            node_id
            for node_id, node in self._nodes.items()
            if node.organization_id == organization_id
            and node.contract_id == contract_id
        ]

        for node_id in to_delete:
            del self._nodes[node_id]

    def delete_many(
        self,
        *,
        organization_id: UUID,
        ids: list[UUID],
    ) -> None:
        for node_id in ids:
            node = self._nodes.get(node_id)
            if node and node.organization_id == organization_id:
                del self._nodes[node_id]

    # =========================================================
    # CHECKS
    # =========================================================

    def exists(
        self,
        *,
        organization_id: UUID,
        contract_node_id: UUID,
    ) -> bool:
        node = self._nodes.get(contract_node_id)
        return bool(node and node.organization_id == organization_id)

    def has_values(
        self,
        *,
        organization_id: UUID,
        contract_id: UUID,
    ) -> bool:
        return any(
            node.organization_id == organization_id
            and node.contract_id == contract_id
            for node in self._nodes.values()
        )

    def node_has_values(
        self,
        *,
        organization_id: UUID,
        contract_node_id: UUID,
    ) -> bool:
        raise NotImplementedError(
            "node_has_values requires InvoiceLineRepository (not available in-memory)"
        )
