from decimal import Decimal
from uuid import uuid4

from contract_costs.model.cost_node import CostNode


class TestCostNode:

    def test_cost_node_root(self) -> None:
        node = CostNode(
            id=uuid4(),
            contract_id=uuid4(),
            parent_id=None,
            budget=Decimal("1000"),
            is_active=True,
            code="ROOT",
            name="Root",
        )

        assert node.parent_id is None

    def test_cost_node_child(self) -> None:
        parent_id = uuid4()
        node = CostNode(
            id=uuid4(),
            contract_id=uuid4(),
            parent_id=parent_id,
            budget=Decimal("500"),
            is_active=True,
            code="CHILD",
            name="Child",
        )

        assert node.parent_id == parent_id