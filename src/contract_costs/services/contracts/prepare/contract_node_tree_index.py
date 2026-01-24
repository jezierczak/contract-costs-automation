from collections import defaultdict
from typing import Iterable
from uuid import UUID

from contract_costs.model.contract_node import ContractNode


class ContractNodeTreeIndex:
    """
    Read-only index of ContractNode tree structure.
    """

    def __init__(self, nodes: Iterable[ContractNode]):
        self.nodes_by_id = {n.id: n for n in nodes}
        self.children_by_parent: dict[UUID | None, list[ContractNode]] = defaultdict(list)

        for node in nodes:
            self.children_by_parent[node.parent_id].append(node)

        for children in self.children_by_parent.values():
            children.sort(key=lambda n: n.code)

    # ---------- queries ----------

    def roots(self) -> list[ContractNode]:
        return self.children_by_parent.get(None, [])

    def children_of(self, node_id: UUID) -> list[ContractNode]:
        return self.children_by_parent.get(node_id, [])

    def is_leaf(self, node: ContractNode) -> bool:
        return not self.children_of(node.id)

    def all_nodes(self) -> list[ContractNode]:
        return list(self.nodes_by_id.values())

    def leaves(self) -> list[ContractNode]:
        return [n for n in self.nodes_by_id.values() if self.is_leaf(n)]

    def postorder(self) -> list[ContractNode]:
        result: list[ContractNode] = []

        def walk(node: ContractNode) -> None:
            for child in self.children_of(node.id):
                walk(child)
            result.append(node)

        for root in self.roots():
            walk(root)

        return result
