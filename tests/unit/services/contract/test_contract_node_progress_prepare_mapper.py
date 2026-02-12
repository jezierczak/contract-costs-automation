from decimal import Decimal
from uuid import uuid4
from datetime import datetime, date

from contract_costs.model.contract import Contract
from contract_costs.model.contract_node import ContractNode
from contract_costs.services.contracts.prepare.mappers.contract_node_progress_prepare_mapper import (
    ContractNodeProgressPrepareMapper,
)


# =========================================
# HELPERS
# =========================================

def make_contract():
    return Contract(
        id=uuid4(),
        organization_id=uuid4(),
        code="C-1",
        name="Test",
        description=None,
        owner=None,
        client=None,
        start_date=None,
        end_date=None,
        budget=None,
        path=None,
        status=None,
        created_at=datetime.now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
    )


def make_node(*, code, parent_id=None, progress=None, is_active=True):
    return ContractNode(
        id=uuid4(),
        organization_id=uuid4(),
        contract_id=uuid4(),
        parent_id=parent_id,
        code=code,
        name=f"Node {code}",
        budget=Decimal("100"),
        quantity=None,
        unit=None,
        is_active=is_active,
        created_at=datetime.now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        progress_history={},
    )


# =========================================
# TESTS
# =========================================

def test_empty_nodes_returns_empty():
    contract = make_contract()

    result = ContractNodeProgressPrepareMapper.map(contract, [])

    assert result == []


def test_only_leaf_nodes_are_returned():
    contract = make_contract()

    root = make_node(code="A")
    child = make_node(code="B", parent_id=root.id)

    rows = ContractNodeProgressPrepareMapper.map(contract, [root, child])

    assert len(rows) == 1
    assert rows[0].code == "B"


def test_progress_is_converted_to_percent():
    contract = make_contract()

    leaf = make_node(code="A")
    leaf.progress_history = {
        date.today(): Decimal("0.75")
    }

    rows = ContractNodeProgressPrepareMapper.map(contract, [leaf])

    assert rows[0].current_progress_percent == Decimal("75")


def test_progress_none_returns_none():
    contract = make_contract()

    leaf = make_node(code="A")
    leaf.progress_history = {}

    rows = ContractNodeProgressPrepareMapper.map(contract, [leaf])

    assert rows[0].current_progress_percent is None


def test_contract_code_is_mapped():
    contract = make_contract()

    leaf = make_node(code="A")

    rows = ContractNodeProgressPrepareMapper.map(contract, [leaf])

    assert rows[0].contract_code == contract.code


def test_is_active_is_mapped():
    contract = make_contract()

    leaf = make_node(code="A", is_active=False)

    rows = ContractNodeProgressPrepareMapper.map(contract, [leaf])

    assert rows[0].is_active is False


def test_dfs_order_of_leafs():
    contract = make_contract()

    root = make_node(code="A")
    child1 = make_node(code="B", parent_id=root.id)
    child2 = make_node(code="C", parent_id=root.id)

    rows = ContractNodeProgressPrepareMapper.map(
        contract,
        [root, child1, child2],
    )

    codes = [r.code for r in rows]

    assert codes == ["B", "C"]
