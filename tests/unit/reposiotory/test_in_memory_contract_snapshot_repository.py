from datetime import date

from contract_costs.common.ids import new_uuid
from tests.builders.contract_snapshot_builder import ContractSnapshotBuilder


def test_add_and_get(contract_snapshot_repo):
    org_id = new_uuid()

    snapshot = (
        ContractSnapshotBuilder()
        .with_organization_id(org_id)
        .build()
    )

    contract_snapshot_repo.add(snapshot)

    result = contract_snapshot_repo.get(
        organization_id=org_id,
        snapshot_id=snapshot.id,
    )

    assert result == snapshot


import pytest

def test_add_duplicate_raises(contract_snapshot_repo):
    snapshot = ContractSnapshotBuilder().build()

    contract_snapshot_repo.add(snapshot)

    with pytest.raises(ValueError):
        contract_snapshot_repo.add(snapshot)


def test_get_isolated_by_org(contract_snapshot_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    snapshot = (
        ContractSnapshotBuilder()
        .with_organization_id(org1)
        .build()
    )

    contract_snapshot_repo.add(snapshot)

    assert contract_snapshot_repo.get(
        organization_id=org2,
        snapshot_id=snapshot.id,
    ) is None


def test_get_by_contract_and_date(contract_snapshot_repo):
    org_id = new_uuid()
    contract_id = new_uuid()
    snapshot_date = date(2024, 1, 1)

    snapshot = (
        ContractSnapshotBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_snapshot_date(snapshot_date)
        .build()
    )

    contract_snapshot_repo.add(snapshot)

    result = contract_snapshot_repo.get_by_contract_and_date(
        organization_id=org_id,
        contract_id=contract_id,
        snapshot_date=snapshot_date,
    )

    assert result == snapshot


def test_list_by_contract_sorted(contract_snapshot_repo):
    org_id = new_uuid()
    contract_id = new_uuid()

    older = (
        ContractSnapshotBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_snapshot_date(date(2024, 1, 1))
        .build()
    )

    newer = (
        ContractSnapshotBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_snapshot_date(date(2025, 1, 1))
        .build()
    )

    contract_snapshot_repo.add(newer)
    contract_snapshot_repo.add(older)

    result = contract_snapshot_repo.list_by_contract(
        organization_id=org_id,
        contract_id=contract_id,
    )

    assert result == [older, newer]


def test_list_all_filters_and_sorts(contract_snapshot_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    s1 = (
        ContractSnapshotBuilder()
        .with_organization_id(org1)
        .with_snapshot_date(date(2024, 1, 1))
        .build()
    )

    s2 = (
        ContractSnapshotBuilder()
        .with_organization_id(org1)
        .with_snapshot_date(date(2025, 1, 1))
        .build()
    )

    s_other = (
        ContractSnapshotBuilder()
        .with_organization_id(org2)
        .build()
    )

    contract_snapshot_repo.add(s2)
    contract_snapshot_repo.add(s1)
    contract_snapshot_repo.add(s_other)

    result = contract_snapshot_repo.list_all(
        organization_id=org1,
    )

    assert result == [s1, s2]
