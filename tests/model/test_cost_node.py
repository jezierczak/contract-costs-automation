from decimal import Decimal
from uuid import uuid4

from contract_costs.model.contract_node import ContractNode
from contract_costs.model.unit_of_measure import UnitOfMeasure


class TestCostNode:

    def test_cost_node_root(self) -> None:
        node = ContractNode(
            id=uuid4(),
            contract_id=uuid4(),
            parent_id=None,
            budget=Decimal("1000"),
            is_active=True,
            code="ROOT",
            name="Root",
            quantity=None,
            unit = None,
            progress=None
        )

        assert node.parent_id is None

    def test_cost_node_child(self) -> None:
        parent_id = uuid4()
        node = ContractNode(
            id=uuid4(),
            contract_id=uuid4(),
            parent_id=parent_id,
            budget=Decimal("500"),
            is_active=True,
            code="CHILD",
            name="Child",
            quantity=Decimal("100"),
            unit=UnitOfMeasure.METER,
            progress=Decimal("0"),
        )

        assert node.parent_id == parent_id