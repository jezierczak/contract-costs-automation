from datetime import date

import pytest

from contract_costs.common.ids import new_uuid
from tests.builders.contract_node_snapshot_builder import ContractNodeSnapshotBuilder
from tests.builders.contract_node_value_snapshot_builder import (
    ContractNodeValueSnapshotBuilder,
)
from tests.builders.contract_snapshot_builder import ContractSnapshotBuilder


def test_contract_snapshot_add_and_get(contract_snapshot_repo_contract):
    org_id = new_uuid()
    snapshot = ContractSnapshotBuilder().with_organization_id(org_id).build()
    contract_snapshot_repo_contract.add(snapshot)

    loaded = contract_snapshot_repo_contract.get(organization_id=org_id, snapshot_id=snapshot.id)
    assert loaded is not None
    assert loaded.id == snapshot.id
    assert loaded.contract_id == snapshot.contract_id


def test_contract_snapshot_duplicate_raises(contract_snapshot_repo_contract):
    snapshot = ContractSnapshotBuilder().build()
    contract_snapshot_repo_contract.add(snapshot)

    with pytest.raises(Exception):
        contract_snapshot_repo_contract.add(snapshot)


def test_contract_snapshot_list_by_contract_sorted(contract_snapshot_repo_contract):
    org_id = new_uuid()
    contract_id = new_uuid()
    older = (
        ContractSnapshotBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_snapshot_date(date(2026, 1, 1))
        .build()
    )
    newer = (
        ContractSnapshotBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_snapshot_date(date(2026, 2, 1))
        .build()
    )
    contract_snapshot_repo_contract.add(newer)
    contract_snapshot_repo_contract.add(older)

    listed = contract_snapshot_repo_contract.list_by_contract(
        organization_id=org_id, contract_id=contract_id
    )
    assert [s.id for s in listed] == [older.id, newer.id]


def test_contract_node_snapshot_add_many_and_list(contract_node_snapshot_repo_contract):
    snapshot_id = new_uuid()
    s1 = ContractNodeSnapshotBuilder().with_snapshot_id(snapshot_id).build()
    s2 = ContractNodeSnapshotBuilder().with_snapshot_id(snapshot_id).build()
    contract_node_snapshot_repo_contract.add_many([s1, s2])

    listed = contract_node_snapshot_repo_contract.list_by_snapshot(snapshot_id)
    assert {s.id for s in listed} == {s1.id, s2.id}


def test_contract_node_value_snapshot_add_many_and_list_by_node_snapshot(
    contract_node_value_snapshot_repo_contract,
):
    node_snapshot_id = new_uuid()
    v1 = ContractNodeValueSnapshotBuilder().with_node_snapshot_id(node_snapshot_id).build()
    v2 = ContractNodeValueSnapshotBuilder().with_node_snapshot_id(node_snapshot_id).build()
    contract_node_value_snapshot_repo_contract.add_many([v1, v2])

    listed = contract_node_value_snapshot_repo_contract.list_by_node_snapshot(node_snapshot_id)
    assert {v.id for v in listed} == {v1.id, v2.id}
