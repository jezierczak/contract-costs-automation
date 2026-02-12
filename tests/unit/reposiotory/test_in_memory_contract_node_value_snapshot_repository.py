from contract_costs.common.ids import new_uuid
from tests.builders.contract_node_value_snapshot_builder import ContractNodeValueSnapshotBuilder


def test_add_many_and_list_all(contract_node_value_snapshot_repo):
    v1 = ContractNodeValueSnapshotBuilder().build()
    v2 = ContractNodeValueSnapshotBuilder().build()

    contract_node_value_snapshot_repo.add_many([v1, v2])

    result = contract_node_value_snapshot_repo.list_all()

    assert set(result) == {v1, v2}

import pytest

def test_add_many_duplicate_raises(contract_node_value_snapshot_repo):
    v = ContractNodeValueSnapshotBuilder().build()

    contract_node_value_snapshot_repo.add_many([v])

    with pytest.raises(ValueError):
        contract_node_value_snapshot_repo.add_many([v])

def test_list_by_node_snapshot(contract_node_value_snapshot_repo):
    node_snapshot_id = new_uuid()

    v1 = (
        ContractNodeValueSnapshotBuilder()
        .with_node_snapshot_id(node_snapshot_id)
        .build()
    )

    v2 = (
        ContractNodeValueSnapshotBuilder()
        .with_node_snapshot_id(node_snapshot_id)
        .build()
    )

    contract_node_value_snapshot_repo.add_many([v1, v2])

    result = contract_node_value_snapshot_repo.list_by_node_snapshot(
        node_snapshot_id
    )

    assert len(result) == 2
    assert v1 in result
    assert v2 in result


def test_list_by_snapshot_uses_node_snapshot_id(contract_node_value_snapshot_repo):
    snapshot_id = new_uuid()

    v = (
        ContractNodeValueSnapshotBuilder()
        .with_node_snapshot_id(snapshot_id)
        .build()
    )

    contract_node_value_snapshot_repo.add_many([v])

    result = contract_node_value_snapshot_repo.list_by_snapshot(snapshot_id)

    assert result == [v]
