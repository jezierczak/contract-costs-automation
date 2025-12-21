from abc import ABC, abstractmethod
from uuid import UUID,uuid4
from contract_costs.model.cost_node import CostNode
from contract_costs.model.cost_node import CostNodeInput


class CostNodeTreeBuilder(ABC):

    @staticmethod
    @abstractmethod
    def build(
        contract_id: UUID,
        node: CostNodeInput,
        parent_id: UUID | None = None,
    ) -> list[CostNode]:
        ...

class DefaultCostNodeTreeBuilder(CostNodeTreeBuilder):

    @staticmethod
    def build(
        contract_id: UUID,
        node_input: CostNodeInput,
        parent_id: UUID | None = None,
    ) -> list[CostNode]:


        node = CostNode(
            id=uuid4(),
            contract_id=contract_id,
            parent_id=parent_id,
            code=node_input['code'],
            name=node_input['name'],
            budget=node_input['budget'],
            is_active=True,
            quantity = node_input['quantity'],
            unit = node_input['unit']
        )

        nodes = [node]

        for child in node_input['children']:
            nodes.extend(
                DefaultCostNodeTreeBuilder.build(contract_id, child, parent_id=node.id)
            )

        return nodes