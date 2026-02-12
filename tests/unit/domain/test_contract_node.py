import uuid
from datetime import datetime, date
from decimal import Decimal

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.contract_node import ContractNode

def build_node(
    *,
    node_id=None,
    parent_id=None,
    budget=None,
    progress_history=None,
    is_active=True,
):
    now = utc_now()

    return ContractNode(
        id=node_id or new_uuid(),
        organization_id=new_uuid(),
        contract_id=new_uuid(),
        created_at=now,
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        code="X",
        name="Node",
        parent_id=parent_id,
        quantity=None,
        unit=None,
        budget=budget,
        is_active=is_active,
        progress_history=progress_history or {},
    )


def test_progress_returns_latest_value():
    d1 = date(2024, 1, 1)
    d2 = date(2024, 2, 1)

    node = build_node(
        progress_history={
            d1: Decimal("0.2"),
            d2: Decimal("0.5"),
        }
    )

    assert node.progress == Decimal("0.5")

def test_progress_returns_none_when_empty():
    node = build_node(progress_history={})
    assert node.progress is None

def test_progress_at_returns_last_before_date():
    d1 = date(2024, 1, 1)
    d2 = date(2024, 2, 1)

    node = build_node(
        progress_history={
            d1: Decimal("0.2"),
            d2: Decimal("0.5"),
        }
    )

    assert node.progress_at(date(2024, 1, 15)) == Decimal("0.2")


def test_progress_at_returns_none_when_no_applicable_date():
    d1 = date(2024, 2, 1)

    node = build_node(
        progress_history={
            d1: Decimal("0.5"),
        }
    )

    assert node.progress_at(date(2024, 1, 1)) is None

def test_calculate_budget_from_leaves_simple_sum():
    parent_id = uuid.uuid4()

    child1 = build_node(
        parent_id=parent_id,
        budget=Decimal("100"),
    )
    child2 = build_node(
        parent_id=parent_id,
        budget=Decimal("200"),
    )

    parent = build_node(
        node_id=parent_id,
        budget=None,
    )

    nodes_by_parent = {
        None: [parent],
        parent_id: [child1, child2],
    }

    result = ContractNode.calculate_budget_from_leaves(
        parent_id, nodes_by_parent
    )

    assert result == Decimal("300")


def test_calculate_budget_ignores_inactive_children():
    parent_id = uuid.uuid4()

    active = build_node(parent_id=parent_id, budget=Decimal("100"))
    inactive = build_node(parent_id=parent_id, budget=Decimal("200"), is_active=False)

    parent = build_node(node_id=parent_id)

    nodes_by_parent = {
        None: [parent],
        parent_id: [active, inactive],
    }

    result = ContractNode.calculate_budget_from_leaves(
        parent_id, nodes_by_parent
    )

    assert result == Decimal("100")


def test_calculate_progress_weighted_average():
    parent_id = uuid.uuid4()

    child1 = build_node(
        parent_id=parent_id,
        budget=Decimal("100"),
        progress_history={date(2024,1,1): Decimal("0.5")},
    )

    child2 = build_node(
        parent_id=parent_id,
        budget=Decimal("300"),
        progress_history={date(2024,1,1): Decimal("1.0")},
    )

    parent = build_node(node_id=parent_id)

    nodes_by_parent = {
        None: [parent],
        parent_id: [child1, child2],
    }

    result = ContractNode.calculate_progress_from_leaves(
        parent_id, nodes_by_parent
    )

    assert result == Decimal("0.875")

def test_calculate_progress_returns_none_when_total_budget_zero():
    parent_id = uuid.uuid4()

    child1 = build_node(
        parent_id=parent_id,
        budget=None,
        progress_history={date(2024,1,1): Decimal("0.5")},
    )

    parent = build_node(node_id=parent_id)

    nodes_by_parent = {
        None: [parent],
        parent_id: [child1],
    }

    result = ContractNode.calculate_progress_from_leaves(
        parent_id, nodes_by_parent
    )

    assert result is None
