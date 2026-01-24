from uuid import UUID
from contract_costs.model.contract_node import ContractNode
from contract_costs.repository.contract_node_repository import ContractNodeRepository


class InMemoryContractNodeRepository(ContractNodeRepository):

    def __init__(self) -> None:
        self._nodes: dict[UUID, ContractNode] = {}

    def add(self, contract_node: ContractNode) -> None:
        self._nodes[contract_node.id] = contract_node

    def add_all(self, contract_nodes: list[ContractNode]) -> None:
        for contract_node in contract_nodes:
            self.add(contract_node)

    def get(self, contract_node_id: UUID) -> ContractNode | None:
        return self._nodes.get(contract_node_id)

    def get_by_code(self, contract_node_code: str) -> ContractNode | None:
        for contract_node in self._nodes.values():
            if contract_node.code == contract_node_code:
                return contract_node
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
        # 1. zbierz wszystkie parent_id
        parent_ids = {
            node.parent_id
            for node in self._nodes.values()
            if node.parent_id is not None
        }

        # 2. liście = node.id nie występuje jako parent_id
        leaf_nodes = [
            node for node in self._nodes.values()
            if node.id not in parent_ids
        ]

        # 3. tylko aktywne kontrakty
        # UWAGA: tu repo NIE powinno znać ContractRepo,
        # więc zakładamy, że CostNode ma info pośrednie
        # albo Contract status jest sprawdzany WYŻEJ
        #
        # Najczystsze rozwiązanie:
        return leaf_nodes

    def delete_by_contract(self, contract_id: UUID) -> None:
        to_delete = [
            node_id
            for node_id, node in self._nodes.items()
            if node.contract_id == contract_id
        ]

        for node_id in to_delete:
            del self._nodes[node_id]

    def delete_many(self, ids: list[UUID]) -> None:
        for i in ids:
            self._nodes.pop(i, None)

    def update(self, contract_node: ContractNode) -> None:
        self._nodes[contract_node.id] = contract_node

    def update_many(self, contract_nodes: list[ContractNode]) -> None:
        for contract_node in contract_nodes:
            self.update(contract_node)

    def exists(self, contract_node_id: UUID) -> bool:
        return contract_node_id in self._nodes

    def has_values(self, contract_id: UUID) -> bool:
        return any(
            node.contract_id == contract_id
            for node in self._nodes.values()
        )

    def node_has_values(self, contract_node_id: UUID) -> bool:
        raise NotImplementedError(
            "node_has_costs requires InvoiceLineRepository"
        )