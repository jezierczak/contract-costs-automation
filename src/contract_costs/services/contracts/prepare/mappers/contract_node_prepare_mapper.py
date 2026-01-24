from collections import defaultdict
from typing import Iterable
from uuid import UUID

from contract_costs.model.contract_node import ContractNode
from contract_costs.services.contracts.prepare.dto.contract_node_prepare_dto import (
    ContractNodePrepareDTO,
)


class ContractNodePrepareMapper:
    """
    Flattens CostNode tree into rows for Excel prepare.
    """

    @staticmethod
    def map(nodes: Iterable[ContractNode]) -> list[ContractNodePrepareDTO]:
        nodes_by_id = {n.id: n for n in nodes}
        children_by_parent = ContractNodePrepareMapper.group_by_parent(nodes)

        rows: list[ContractNodePrepareDTO] = []

        def walk(node: ContractNode) -> None:
            parent_code = None
            if node.parent_id:
                parent = nodes_by_id.get(node.parent_id)
                parent_code = parent.code if parent else None

            rows.append(
                ContractNodePrepareDTO(
                    code=node.code,
                    name=node.name,
                    parent_code=parent_code,
                    budget=node.budget,
                    quantity=node.quantity,
                    unit=node.unit.value if node.unit else None,
                    is_active=node.is_active,
                )
            )

            for child in children_by_parent.get(node.id, []):
                walk(child)

        # roots only
        for root in children_by_parent.get(None, []):
            walk(root)

        return rows

    @staticmethod
    def group_by_parent(
        nodes: Iterable[ContractNode],
    ) -> dict[UUID | None, list[ContractNode]]:
        grouped: dict[UUID | None, list[ContractNode]] = defaultdict(list)

        for node in nodes:
            grouped[node.parent_id].append(node)

        for children in grouped.values():
            children.sort(key=lambda n: n.code)

        return grouped
