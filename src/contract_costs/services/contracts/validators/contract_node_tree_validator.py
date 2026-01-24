from typing import Dict, Set
from uuid import UUID

from contract_costs.model.contract_node import ContractNode


class ContractNodeEntityValidator:
    """
    Validates ContractNode entities before persisting to repository.
    """

    def validate(self, nodes: list[ContractNode]) -> None:
        if not nodes:
            raise ValueError("No contract nodes provided")

        self._validate_single_contract(nodes)
        self._validate_unique_codes(nodes)
        self._validate_single_root(nodes)
        self._validate_parents_exist(nodes)
        self._validate_no_cycles(nodes)

    # ---------------- private ----------------
    @staticmethod
    def _validate_single_contract( nodes: list[ContractNode]) -> None:
        contract_ids = {n.contract_id for n in nodes}
        if len(contract_ids) != 1:
            raise ValueError("Contract nodes belong to multiple contracts")

    @staticmethod
    def _validate_unique_codes( nodes: list[ContractNode]) -> None:
        codes = [n.code for n in nodes]
        duplicates = {c for c in codes if codes.count(c) > 1}
        if duplicates:
            raise ValueError(f"Duplicate contract node codes: {duplicates}")

    @staticmethod
    def _validate_single_root( nodes: list[ContractNode]) -> None:
        roots = [n for n in nodes if n.parent_id is None]

        if len(roots) != 1:
            raise ValueError(
                f"Exactly one ROOT node required, found {len(roots)}"
            )

        root = roots[0]
        if root.code != "ROOT":
            raise ValueError("Root node must have code='ROOT'")

    @staticmethod
    def _validate_parents_exist( nodes: list[ContractNode]) -> None:
        node_ids: Set[UUID] = {n.id for n in nodes}

        for node in nodes:
            if node.parent_id and node.parent_id not in node_ids:
                raise ValueError(
                    f"Parent id '{node.parent_id}' not found for node '{node.code}'"
                )

            if node.parent_id == node.id:
                raise ValueError(f"Node '{node.code}' cannot be its own parent")

    @staticmethod
    def _validate_no_cycles( nodes: list[ContractNode]) -> None:
        by_id: Dict[UUID, ContractNode] = {n.id: n for n in nodes}

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
