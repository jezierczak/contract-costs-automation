import uuid
from decimal import Decimal

from contract_costs.builders.cost_node_tree_builder import DefaultCostNodeTreeBuilder


class TestCostNodeTreeBuilder:


    def test_default_cost_node_tree_builder_creates_tree(self,cost_node_tree_1) -> None:
        contract_id = uuid.uuid4()

        node_tree_builder = DefaultCostNodeTreeBuilder()

        nodes = node_tree_builder.build(contract_id,cost_node_tree_1)

        # --- liczba węzłów ---
        assert len(nodes) == 3

        # --- wszystkie należą do kontraktu ---
        assert all(node.contract_id == contract_id for node in nodes)

        # --- dokładnie jeden root ---
        roots = [n for n in nodes if n.parent_id is None]

        assert len(roots) == 1

        root = roots[0]
        assert root.code == "WYB"
        assert root.name == "wyburzenia"
        assert root.budget == Decimal("100000")

        # --- dzieci ---
        children = [n for n in nodes if n.parent_id == root.id]
        assert len(children) == 2

        child_codes = {c.code for c in children}
        assert child_codes == {"WYB_SCI", "WYB_POS"}

        budgets = {c.code: c.budget for c in children}
        assert budgets["WYB_SCI"] == Decimal("50000")
        assert budgets["WYB_POS"] == Decimal("50000")





