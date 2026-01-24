from decimal import Decimal

from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode
from contract_costs.services.contracts.prepare.dto.contract_node_progress_prepare_dto import (
    ContractNodeProgressPrepareDTO,
)

from contract_costs.services.contracts.prepare.contract_node_tree_index import ContractNodeTreeIndex

class ContractNodeProgressPrepareMapper:
    """
    Flattens ContractNode tree into leaf rows for progress editing.
    """

    @staticmethod
    def map(
        contract: Contract,
        nodes: list[ContractNode],
    ) -> list[ContractNodeProgressPrepareDTO]:

        tree = ContractNodeTreeIndex(nodes)

        rows: list[ContractNodeProgressPrepareDTO] = []

        def walk(node: ContractNode) -> None:
            if tree.is_leaf(node):
                rows.append(
                    ContractNodeProgressPrepareDTO(
                        contract_code=contract.code,
                        contract_node_id=node.id,
                        code=node.code,
                        name=node.name,
                        budget=node.budget,
                        current_progress_percent=(
                            node.progress * Decimal("100")
                            if node.progress is not None
                            else None
                        ),
                        new_progress_percent=None,
                        is_active=node.is_active,
                    )
                )
                return

            for child in tree.children_of(node.id):
                walk(child)

        for root in tree.roots():
            walk(root)

        return rows