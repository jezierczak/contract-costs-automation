from contract_costs.common.ids import new_uuid
from tests.builders.contract_node_snapshot_builder import ContractNodeSnapshotBuilder


def test_add_many_and_get(contract_node_snapshot_repo):
    snapshot = ContractNodeSnapshotBuilder().build()

    contract_node_snapshot_repo.add_many([snapshot])

    result = contract_node_snapshot_repo.get(snapshot.id)

    assert result == snapshot


def test_add_many_duplicate_raises(contract_node_snapshot_repo):
    snapshot = ContractNodeSnapshotBuilder().build()

    contract_node_snapshot_repo.add_many([snapshot])

    with pytest.raises(ValueError):
        contract_node_snapshot_repo.add_many([snapshot])

def test_list_by_snapshot(contract_node_snapshot_repo):
    snapshot_id = new_uuid()

    s1 = (
        ContractNodeSnapshotBuilder()
        .with_snapshot_id(snapshot_id)
        .build()
    )

    s2 = (
        ContractNodeSnapshotBuilder()
        .with_snapshot_id(snapshot_id)
        .build()
    )

    contract_node_snapshot_repo.add_many([s1, s2])

    result = contract_node_snapshot_repo.list_by_snapshot(snapshot_id)

    assert len(result) == 2
    assert s1 in result
    assert s2 in result


def test_list_all(contract_node_snapshot_repo):
    s1 = ContractNodeSnapshotBuilder().build()
    s2 = ContractNodeSnapshotBuilder().build()

    contract_node_snapshot_repo.add_many([s1, s2])

    result = contract_node_snapshot_repo.list_all()

    assert len(result) == 2
    assert s1 in result
    assert s2 in result


import pytest

def test_get_root_not_supported(contract_node_snapshot_repo):
    with pytest.raises(NotImplementedError):
        contract_node_snapshot_repo.get_root_by_snapshot(new_uuid())
