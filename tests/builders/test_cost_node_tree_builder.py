import uuid
from decimal import Decimal

from contract_costs.builders.contract_node_tree_builder import DefaultContractNodeTreeBuilder


class TestCostNodeTreeBuilder:


    def test_default_cost_node_tree_builder_creates_tree(self,cost_node_tree_1) -> None:
        contract_id = uuid.uuid4()

        node_tree_builder = DefaultContractNodeTreeBuilder()

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


def test_default_cost_node_tree_builder_creates_tree(
  cost_node_tree_1
) -> None:
    contract_id = uuid.uuid4()

    node_tree_builder = DefaultContractNodeTreeBuilder()

    nodes = node_tree_builder.build(contract_id, [cost_node_tree_1])

    # --- liczba węzłów ---
    assert len(nodes) == 4

    # --- wszystkie należą do kontraktu ---
    assert all(node.contract_id == contract_id for node in nodes)

    # --- dokładnie jeden root ---
    roots = [n for n in nodes if n.parent_id is None]
    assert len(roots) == 1

    root = roots[0]
    assert root.code == "ROOT"

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

def test_builder_preserves_progress_on_soft_update(
  cost_node_tree_1
) -> None:
    contract_id = uuid.uuid4()

    builder = DefaultContractNodeTreeBuilder()

    # --- pierwszy build (create) ---
    original_nodes = builder.build(contract_id, [cost_node_tree_1])

    # symulujemy zapis progressu na liściach
    existing_nodes = {}
    for node in original_nodes:
        if node.budget is not None:  # liść
            node.progress = Decimal("0.25")
        existing_nodes[node.code] = node

    # --- drugi build (soft update) ---
    updated_nodes = builder.build(
        contract_id,
        [cost_node_tree_1],
        existing_nodes=existing_nodes,
    )

    updated_by_code = {n.code: n for n in updated_nodes}

    # --- progress został zachowany ---
    assert updated_by_code["WYB_SCI"].progress == Decimal("0.25")
    assert updated_by_code["WYB_POS"].progress == Decimal("0.25")

    # --- parenty nadal nie mają progressu ---
    assert updated_by_code["ROOT"].progress is None

def test_builder_resets_progress_on_hard_update(
  cost_node_tree_1
) -> None:
    contract_id = uuid.uuid4()

    builder = DefaultContractNodeTreeBuilder()

    original_nodes = builder.build(contract_id, [cost_node_tree_1])

    # ustawiamy progress
    for node in original_nodes:
        if node.budget is not None:
            node.progress = Decimal("0.75")

    # --- hard update: bez existing_nodes ---
    rebuilt_nodes = builder.build(contract_id, [cost_node_tree_1])

    # --- progress MUSI być None ---
    for node in rebuilt_nodes:
        assert node.progress is None
