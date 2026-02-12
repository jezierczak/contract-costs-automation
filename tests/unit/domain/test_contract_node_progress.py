from decimal import Decimal
from uuid import uuid4
from datetime import date
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
    progress_history=None,
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
        progress_history=progress_history or {},
    )


def build_index(nodes):
    nodes_by_parent = defaultdict(list)
    for n in nodes:
        nodes_by_parent[n.parent_id].append(n)
    return nodes_by_parent


# --------------------------------------------------
# LEAF PROGRESS
# --------------------------------------------------

def test_leaf_progress():
    contract_id = uuid4()
    org_id = uuid4()

    leaf = make_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="A",
        budget=Decimal("100"),
        progress_history={date(2025, 1, 1): Decimal("0.5")},
    )

    nodes_by_parent = build_index([leaf])

    result = ContractNode.calculate_progress_from_leaves(
        leaf.id,
        nodes_by_parent,
    )

    assert result == Decimal("0.5")


# --------------------------------------------------
# SIMPLE WEIGHTED AVERAGE
# --------------------------------------------------

def test_weighted_average_progress():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_node(contract_id=contract_id, organization_id=org_id, code="ROOT")

    child1 = make_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="1",
        parent_id=root.id,
        budget=Decimal("100"),
        progress_history={date(2025, 1, 1): Decimal("0.5")},
    )

    child2 = make_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="2",
        parent_id=root.id,
        budget=Decimal("300"),
        progress_history={date(2025, 1, 1): Decimal("1.0")},
    )

    nodes_by_parent = build_index([root, child1, child2])

    result = ContractNode.calculate_progress_from_leaves(
        root.id,
        nodes_by_parent,
    )

    # (0.5*100 + 1.0*300) / 400 = 0.875
    assert result == Decimal("0.875")


# --------------------------------------------------
# IGNORE CHILD WITHOUT PROGRESS
# --------------------------------------------------

def test_ignore_child_without_progress():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_node(contract_id=contract_id, organization_id=org_id, code="ROOT")

    child1 = make_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="1",
        parent_id=root.id,
        budget=Decimal("100"),
        progress_history={},  # brak progressu
    )

    child2 = make_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="2",
        parent_id=root.id,
        budget=Decimal("100"),
        progress_history={date(2025, 1, 1): Decimal("1.0")},
    )

    nodes_by_parent = build_index([root, child1, child2])

    result = ContractNode.calculate_progress_from_leaves(
        root.id,
        nodes_by_parent,
    )

    # tylko child2 się liczy
    assert result == Decimal("1.0")


# --------------------------------------------------
# ZERO TOTAL BUDGET
# --------------------------------------------------

def test_zero_total_budget_returns_none():
    contract_id = uuid4()
    org_id = uuid4()

    root = make_node(contract_id=contract_id, organization_id=org_id, code="ROOT")

    child = make_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="1",
        parent_id=root.id,
        budget=None,
        progress_history={date(2025, 1, 1): Decimal("1.0")},
    )

    nodes_by_parent = build_index([root, child])

    result = ContractNode.calculate_progress_from_leaves(
        root.id,
        nodes_by_parent,
    )

    assert result is None


# --------------------------------------------------
# PROGRESS AT DATE
# --------------------------------------------------

def test_progress_at_specific_date():
    contract_id = uuid4()
    org_id = uuid4()

    leaf = make_node(
        contract_id=contract_id,
        organization_id=org_id,
        code="A",
        budget=Decimal("100"),
        progress_history={
            date(2025, 1, 1): Decimal("0.2"),
            date(2025, 2, 1): Decimal("0.8"),
        },
    )

    nodes_by_parent = build_index([leaf])

    result = ContractNode.calculate_progress_from_leaves_at(
        leaf.id,
        nodes_by_parent,
        date(2025, 1, 15),
    )

    # powinien wziąć 0.2 (ostatni <= data)
    assert result == Decimal("0.2")
