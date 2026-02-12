from decimal import Decimal
from unittest.mock import MagicMock
from uuid import uuid4

from contract_costs.model.contract_node import ContractNode
from contract_costs.services.contracts.prepare.mappers.contract_node_prepare_mapper import (
    ContractNodePrepareMapper,
)


def make_node(*, code, parent_id=None, budget=None):
    return ContractNode(
        id=uuid4(),
        organization_id=uuid4(),
        contract_id=uuid4(),
        parent_id=parent_id,
        code=code,
        name=f"Node {code}",
        budget=budget,
        quantity=None,
        unit=None,
        is_active=True,
        created_at=None,
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        progress_history={},
    )


# =========================================
# BASIC
# =========================================

def test_empty_list_returns_empty():
    result = ContractNodePrepareMapper.map([])
    assert result == []


def test_single_root():
    root = make_node(code="A", budget=Decimal("100"))

    rows = ContractNodePrepareMapper.map([root])

    assert len(rows) == 1
    assert rows[0].code == "A"
    assert rows[0].parent_code is None
    assert rows[0].budget == Decimal("100")


# =========================================
# TREE STRUCTURE
# =========================================

def test_root_with_children_sets_parent_code():
    root = make_node(code="A")
    child = make_node(code="B", parent_id=root.id)

    rows = ContractNodePrepareMapper.map([root, child])

    assert len(rows) == 2

    root_row = next(r for r in rows if r.code == "A")
    child_row = next(r for r in rows if r.code == "B")

    assert root_row.parent_code is None
    assert child_row.parent_code == "A"


def test_nested_tree_dfs_order():
    root = make_node(code="A")
    child1 = make_node(code="B", parent_id=root.id)
    child2 = make_node(code="C", parent_id=child1.id)

    rows = ContractNodePrepareMapper.map([root, child1, child2])

    codes = [r.code for r in rows]

    # DFS preorder: A -> B -> C
    assert codes == ["A", "B", "C"]


# =========================================
# MULTIPLE ROOTS
# =========================================

def test_multiple_roots():
    root1 = make_node(code="A")
    root2 = make_node(code="B")

    rows = ContractNodePrepareMapper.map([root1, root2])

    codes = [r.code for r in rows]

    assert "A" in codes
    assert "B" in codes
    assert all(r.parent_code is None for r in rows)


def test_unit_is_mapped_to_value():
    node = make_node(code="A")
    node.unit = MagicMock(value="m2")

    rows = ContractNodePrepareMapper.map([node])

    assert rows[0].unit == "m2"
