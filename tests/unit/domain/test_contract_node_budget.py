from decimal import Decimal
from uuid import uuid4
from collections import defaultdict

from contract_costs.model.contract_node import ContractNode
from contract_costs.common.time import utc_now


def make_node(
    *,
    contract_id,
    organization_id,
    code,
    budget=None,
    parent_id=None,
    is_active=True,
):
    now = utc_now()

    return ContractNode(
        id=uuid4(),
        organization_id=organization_id,
        created_at=now,
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        contract_id=contract_id,
        code=code,
        name=code,
        parent_id=parent_id,
        quantity=None,
        unit=None,
        budget=budget,
        is_active=is_active,
        progress_history={},
    )


def build_index(nodes):
    nodes_by_parent = defaultdict(list)
    for n in nodes:
        nodes_by_parent[n.parent_id].append(n)
    return nodes_by_parent


# --------------------------------------------------
# LEAF
# --------------------------------------------------

def test_leaf_returns_own_budget():
    contract_id = uuid4()
    org_id = uuid4()

    leaf = make_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="A",
        budget=Decimal("100"),
    )

    nodes_by_parent = build_index([leaf])

    result = ContractNode.calculate_budget_from_leaves(
        leaf.id,
        nodes_by_parent,
    )

    assert result == Decimal("100")


# --------------------------------------------------
# SIMPLE TREE SUM
# --------------------------------------------------

def test_parent_sums_children():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_node(contract_id=contract_id, organization_id=org_id, code="ROOT")
    child1 = make_node(contract_id=contract_id, organization_id=org_id, code="1", parent_id=root.id, budget=Decimal("100"))
    child2 = make_node(contract_id=contract_id, organization_id=org_id, code="2", parent_id=root.id, budget=Decimal("200"))

    nodes_by_parent = build_index([root, child1, child2])

    result = ContractNode.calculate_budget_from_leaves(
        root.id,
        nodes_by_parent,
    )

    assert result == Decimal("300")


# --------------------------------------------------
# MULTI LEVEL
# --------------------------------------------------

def test_multilevel_budget():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_node(contract_id=contract_id, organization_id=org_id, code="ROOT")
    child = make_node(contract_id=contract_id, organization_id=org_id, code="1", parent_id=root.id)
    leaf1 = make_node(contract_id=contract_id, organization_id=org_id, code="1.1", parent_id=child.id, budget=Decimal("50"))
    leaf2 = make_node(contract_id=contract_id, organization_id=org_id, code="1.2", parent_id=child.id, budget=Decimal("150"))

    nodes_by_parent = build_index([root, child, leaf1, leaf2])

    result = ContractNode.calculate_budget_from_leaves(
        root.id,
        nodes_by_parent,
    )

    assert result == Decimal("200")


# --------------------------------------------------
# IGNORE INACTIVE
# --------------------------------------------------

def test_ignore_inactive_children():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_node(contract_id=contract_id, organization_id=org_id, code="ROOT")
    active = make_node(contract_id=contract_id, organization_id=org_id, code="1", parent_id=root.id, budget=Decimal("100"))
    inactive = make_node(contract_id=contract_id, organization_id=org_id, code="2", parent_id=root.id, budget=Decimal("500"), is_active=False)

    nodes_by_parent = build_index([root, active, inactive])

    result = ContractNode.calculate_budget_from_leaves(
        root.id,
        nodes_by_parent,
    )

    assert result == Decimal("100")


# --------------------------------------------------
# NONE BUDGET LEAF
# --------------------------------------------------

def test_leaf_with_none_budget_returns_zero():
    contract_id = uuid4()
    org_id = uuid4()

    leaf = make_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="A",
        budget=None,
    )

    nodes_by_parent = build_index([leaf])

    result = ContractNode.calculate_budget_from_leaves(
        leaf.id,
        nodes_by_parent,
    )

    assert result == Decimal("0")
