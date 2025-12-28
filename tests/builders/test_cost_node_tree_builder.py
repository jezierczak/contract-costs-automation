import uuid
from decimal import Decimal

from contract_costs.builders.cost_node_tree_builder import DefaultCostNodeTreeBuilder


class TestCostNodeTreeBuilder:


    def test_default_cost_node_tree_builder_creates_tree(self,cost_node_tree_1) -> None:
        contract_id = uuid.uuid4()

        node_tree_builder = DefaultCostNodeTreeBuilder()

        nodes = node_tree_builder.build(contract_id,[cost_node_tree_1])

        # --- liczba węzłów ---
        assert len(nodes) == 4

        # --- wszystkie należą do kontraktu ---
        assert all(node.contract_id == contract_id for node in nodes)

        # --- dokładnie jeden root ---
        roots = [n for n in nodes if n.parent_id is None]

        assert len(roots) == 1

        root = roots[0]
        assert root.code == "ROOT"

        # assert roots[1].code == "WYB"
        # assert roots[1].name == "wyburzenia"
        # assert roots[1].budget == Decimal("100000")

        # --- dzieci ---
        children_lvl1 = [n for n in nodes if n.parent_id == root.id]
        assert len(children_lvl1) == 1

        children_lvl2 = [
            n
            for parent in children_lvl1
            for n in nodes
            if n.parent_id == parent.id
        ]

        budgets = {c.code: c.budget for c in children_lvl2}
        assert budgets["WYB_SCI"] == Decimal("50000")
        assert budgets["WYB_POS"] == Decimal("50000")





