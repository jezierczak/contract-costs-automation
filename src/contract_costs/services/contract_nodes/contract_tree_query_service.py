from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.contract_nodes.dto.contract_tree_node_dto import (
    ContractTreeNodeDTO,
)
from contract_costs.services.contract_nodes.dto.contract_tree_query import (
    ContractTreeQuery,
)
from contract_costs.services.contracts.prepare.contract_node_tree_index import (
    ContractNodeTreeIndex,
)


class ContractTreeQueryService(
    ActionHandler[ContractTreeQuery, list[ContractTreeNodeDTO]]
):

    def execute(self, *, action, uow):

        node_repo = uow.contract_nodes

        nodes = node_repo.list_by_contract(
            organization_id=action.organization_id,
            contract_id=action.contract_id,
        )

        tree = ContractNodeTreeIndex(nodes)

        # 🔥 ważne — jedno zapytanie
        nodes_with_values = set(
            node_repo.list_nodes_with_values(
                organization_id=action.organization_id,
                contract_id=action.contract_id,
            )
        )

        result: list[ContractTreeNodeDTO] = []

        for node, depth in tree.flatten():

            is_leaf = tree.is_leaf(node)
            has_values = node.id in nodes_with_values
            is_root = node.parent_id is None
            # if node.code == "ROOT":
            #     continue

            can_remove = (
                    not is_root
                    and is_leaf
                    and not has_values
            )

            can_add_child = not (is_leaf and has_values)

            result.append(
                ContractTreeNodeDTO(
                    node_id=node.id,
                    parent_id=node.parent_id,
                    code=node.code,
                    name=node.name,
                    quantity=node.quantity,
                    unit=node.unit,
                    planned_budget=node.budget,
                    is_active=node.is_active,

                    depth=depth,

                    is_leaf=is_leaf,
                    has_values=has_values,
                    can_add_child=can_add_child,
                    can_remove=can_remove,
                )
            )

        return result