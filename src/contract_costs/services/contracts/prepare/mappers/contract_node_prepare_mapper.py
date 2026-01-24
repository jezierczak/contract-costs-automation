from contract_costs.model.contract_node import ContractNode
from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex
from contract_costs.services.contracts.prepare.dto.contract_node_prepare_dto import (
    ContractNodePrepareDTO,
)


class ContractNodePrepareMapper:
    """
    Flattens CostNode tree into rows for Excel prepare.
    """

    @staticmethod
    def map(nodes: list[ContractNode]) -> list[ContractNodePrepareDTO]:
        tree = ContractNodeTreeIndex(nodes)

        rows: list[ContractNodePrepareDTO] = []

        def walk(node: ContractNode) -> None:
            parent_code = None
            if node.parent_id:
                parent = tree.nodes_by_id.get(node.parent_id)
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

            for child in tree.children_of(node.id):
                walk(child)

        for root in tree.roots():
            walk(root)

        return rows
