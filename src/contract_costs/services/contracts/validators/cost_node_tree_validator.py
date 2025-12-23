from typing import Dict, Set
from uuid import UUID

from contract_costs.model.cost_node import CostNode


class CostNodeEntityValidator:
    """
    Validates CostNode entities before persisting to repository.
    """

    def validate(self, nodes: list[CostNode]) -> None:
        if not nodes:
            raise ValueError("No cost nodes provided")

        self._validate_single_contract(nodes)
        self._validate_unique_codes(nodes)
        self._validate_single_root(nodes)
        self._validate_parents_exist(nodes)
        self._validate_no_cycles(nodes)

    # ---------------- private ----------------

    def _validate_single_contract(self, nodes: list[CostNode]) -> None:
        contract_ids = {n.contract_id for n in nodes}
        if len(contract_ids) != 1:
            raise ValueError("Cost nodes belong to multiple contracts")

    def _validate_unique_codes(self, nodes: list[CostNode]) -> None:
        codes = [n.code for n in nodes]
        duplicates = {c for c in codes if codes.count(c) > 1}
        if duplicates:
            raise ValueError(f"Duplicate cost node codes: {duplicates}")

    def _validate_single_root(self, nodes: list[CostNode]) -> None:
        roots = [n for n in nodes if n.parent_id is None]

        if len(roots) != 1:
            raise ValueError(
                f"Exactly one ROOT node required, found {len(roots)}"
            )

        root = roots[0]
        if root.code != "ROOT":
            raise ValueError("Root node must have code='ROOT'")

    def _validate_parents_exist(self, nodes: list[CostNode]) -> None:
        node_ids: Set[UUID] = {n.id for n in nodes}

        for node in nodes:
            if node.parent_id and node.parent_id not in node_ids:
                raise ValueError(
                    f"Parent id '{node.parent_id}' not found for node '{node.code}'"
                )

            if node.parent_id == node.id:
                raise ValueError(f"Node '{node.code}' cannot be its own parent")

    def _validate_no_cycles(self, nodes: list[CostNode]) -> None:
        by_id: Dict[UUID, CostNode] = {n.id: n for n in nodes}

        for node in nodes:
            visited: Set[UUID] = set()
            current = node

            while current.parent_id:
                if current.parent_id in visited:
                    raise ValueError(
                        f"Cycle detected starting at node '{node.code}'"
                    )

                visited.add(current.id)
                current = by_id[current.parent_id]
