from datetime import date
from uuid import uuid4

import pytest

from contract_costs.services.snapshots.create_contract_snapshot_service import (
    CreateContractSnapshotService,
)
from contract_costs.services.snapshots.dto.create_contract_snapshot_command import (
    CreateContractSnapshotCommand,
)
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.builders.contract_snapshot_builder import ContractSnapshotBuilder


def _cmd(*, organization_id, contract_id, snapshot_date):
    return CreateContractSnapshotCommand(
        organization_id=organization_id,
        actor_user_id=uuid4(),
        contract_id=contract_id,
        snapshot_date=snapshot_date,
    )


def test_snapshot_service_returns_existing_snapshot_for_same_date():
    uow = InMemoryUnitOfWork()
    org_id = uuid4()
    contract_id = uuid4()
    snapshot_date = date(2026, 2, 16)

    existing = (
        ContractSnapshotBuilder()
        .with_organization_id(org_id)
        .with_contract_id(contract_id)
        .with_snapshot_date(snapshot_date)
        .build()
    )
    uow.contract_snapshots.add(existing)

    service = CreateContractSnapshotService()
    snapshot, created = service.execute(
        action=_cmd(organization_id=org_id, contract_id=contract_id, snapshot_date=snapshot_date),
        uow=uow,
    )

    assert snapshot == existing
    assert created is False


def test_snapshot_service_raises_when_contract_missing():
    service = CreateContractSnapshotService()

    with pytest.raises(ValueError, match="not found"):
        service.execute(
            action=_cmd(
                organization_id=uuid4(),
                contract_id=uuid4(),
                snapshot_date=date(2026, 2, 16),
            ),
            uow=InMemoryUnitOfWork(),
        )
