import pytest
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.contract_node import ContractNode
from decimal import Decimal


def build_node(
    *,
    organization_id,
    contract_id,
    parent_id=None,
    code="N1",
    budget=None,
):
    return ContractNode(
        id=new_uuid(),
        organization_id=organization_id,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        contract_id=contract_id,
        code=code,
        name="Node",
        parent_id=parent_id,
        quantity=None,
        unit=None,
        budget=budget,
        is_active=True,
        progress_history={},
    )

def test_add_and_get_node(contract_node_repo):
    org_id = new_uuid()
    contract_id = new_uuid()

    node = build_node(
        organization_id=org_id,
        contract_id=contract_id,
    )

    contract_node_repo.add(node)

    result = contract_node_repo.get(
        organization_id=org_id,
        contract_node_id=node.id,
    )

    assert result == node

def test_get_isolated_by_org(contract_node_repo):
    org1 = new_uuid()
    org2 = new_uuid()
    contract_id = new_uuid()

    node = build_node(
        organization_id=org1,
        contract_id=contract_id,
    )

    contract_node_repo.add(node)

    result = contract_node_repo.get(
        organization_id=org2,
        contract_node_id=node.id,
    )

    assert result is None

from contract_costs.model.contract_node_progress import ContractNodeProgress
from datetime import date
from decimal import Decimal

def test_add_progress_updates_node(contract_node_repo):
    org_id = new_uuid()
    contract_id = new_uuid()

    node = build_node(
        organization_id=org_id,
        contract_id=contract_id,
    )

    contract_node_repo.add(node)

    progress = ContractNodeProgress(
        id=new_uuid(),
        organization_id=org_id,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        contract_node_id=node.id,
        progress_date=date(2024, 1, 1),
        progress=Decimal("0.5"),
    )

    contract_node_repo.add_progress(progress)

    assert node.progress == Decimal("0.5")

import pytest

def test_add_progress_cross_org_raises(contract_node_repo):
    org1 = new_uuid()
    org2 = new_uuid()
    contract_id = new_uuid()

    node = build_node(
        organization_id=org1,
        contract_id=contract_id,
    )

    contract_node_repo.add(node)

    progress = ContractNodeProgress(
        id=new_uuid(),
        organization_id=org2,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        contract_node_id=node.id,
        progress_date=date(2024, 1, 1),
        progress=Decimal("0.5"),
    )

    with pytest.raises(PermissionError):
        contract_node_repo.add_progress(progress)



def test_list_by_parent(contract_node_repo):
    org_id = new_uuid()
    contract_id = new_uuid()

    parent = build_node(
        organization_id=org_id,
        contract_id=contract_id,
    )

    child = build_node(
        organization_id=org_id,
        contract_id=contract_id,
        parent_id=parent.id,
    )

    contract_node_repo.add_all([parent, child])

    result = contract_node_repo.list_by_parent(
        organization_id=org_id,
        parent_id=parent.id,
    )

    assert result == [child]

def test_delete_by_contract(contract_node_repo):
    org_id = new_uuid()
    contract_id = new_uuid()

    node = build_node(
        organization_id=org_id,
        contract_id=contract_id,
    )

    contract_node_repo.add(node)

    contract_node_repo.delete_by_contract(
        organization_id=org_id,
        contract_id=contract_id,
    )

    assert not contract_node_repo.exists(
        organization_id=org_id,
        contract_node_id=node.id,
    )


def test_list_leaf_nodes(contract_node_repo):
    org_id = new_uuid()
    contract_id = new_uuid()

    parent = build_node(
        organization_id=org_id,
        contract_id=contract_id,
    )

    child = build_node(
        organization_id=org_id,
        contract_id=contract_id,
        parent_id=parent.id,
    )

    contract_node_repo.add_all([parent, child])

    result = contract_node_repo.list_leaf_nodes_for_active_contracts(
        organization_id=org_id,
    )

    assert child in result
    assert parent not in result
