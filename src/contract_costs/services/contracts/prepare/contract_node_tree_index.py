from collections import defaultdict
from typing import Iterable
from uuid import UUID

from contract_costs.model.contract_node import ContractNode
from contract_costs.services.contracts.prepare.tree_node import TreeNode


class ContractNodeTreeIndex[T:TreeNode]:
    """
    Read-only index of ContractNode tree structure.
    """

    def __init__(self, nodes: Iterable[T]):
        self.nodes_by_id = {n.id: n for n in nodes}
        self.children_by_parent: dict[UUID | None, list[T]] = defaultdict(list)

        for node in nodes:
            self.children_by_parent[node.parent_id].append(node)

        for children in self.children_by_parent.values():
            children.sort(key=lambda n: n.code)

    # ---------- queries ----------

    def roots(self) -> list[T]:
        return self.children_by_parent.get(None, [])

    def children_of(self, node_id: UUID) -> list[T]:
        return self.children_by_parent.get(node_id, [])

    def is_leaf(self, node: T) -> bool:
        return not self.children_of(node.id)

    def all_nodes(self) -> list[T]:
        return list(self.nodes_by_id.values())

    def leaves(self) -> list[T]:
        return [n for n in self.nodes_by_id.values() if self.is_leaf(n)]

    def postorder(self) -> list[T]:
        result: list[T] = []

        def walk(node: T) -> None:
            for child in self.children_of(node.id):
                walk(child)
            result.append(node)

        for root in self.roots():
            walk(root)

        return result

    def flatten(self) -> list[tuple[T, int]]:
        """
        Returns flat list of (node, depth)
        for easy tree rendering in UI.
        """

        result: list[tuple[T, int]] = []

        def walk(node: T, depth: int) -> None:
            result.append((node, depth))
            for child in self.children_of(node.id):
                walk(child, depth + 1)

        for root in self.roots():
            walk(root, 0)

        return result

    def depth_of(self, node_id):
        depth = 0
        current = self.nodes_by_id[node_id]

        while current.parent_id is not None:
            depth += 1
            current = self.nodes_by_id[current.parent_id]

        return depth

    def preorder(self) -> list[T]:
        result: list[T] = []

        def walk(node: T) -> None:
            result.append(node)
            for child in self.children_of(node.id):
                walk(child)

        for root in self.roots():
            walk(root)

        return result