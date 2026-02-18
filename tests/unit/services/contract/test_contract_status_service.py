import pytest
from datetime import datetime
from uuid import uuid4


from contract_costs.services.contracts.apply.command.set_contract_status_command import (
    SetContractStatusCommand,
)
from contract_costs.model.contract import ContractStatus
from contract_costs.services.contracts.apply.set_contract_status_service import SetContractStatusService
from tests.builders.contract_builder import ContractBuilder
from tests.builders.company_builder import CompanyBuilder
from contract_costs.model.company import CompanyType


def test_set_contract_status_updates_status(
    contract_repo,
    uow,
):
    org_id = uuid4()
    user_id = uuid4()

    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(CompanyBuilder().with_role(CompanyType.OWN).build())
        .with_status(ContractStatus.ACTIVE)
        .build()
    )

    contract_repo.add(contract)

    fixed_time = datetime(2024, 1, 1)

    service = SetContractStatusService(
        clock=lambda: fixed_time,
    )

    cmd = SetContractStatusCommand(
        organization_id=org_id,
        contract_id=contract.id,
        actor_user_id=user_id,
        new_status=ContractStatus.COMPLETED,
    )

    service.execute(action=cmd, uow=uow)

    updated = contract_repo.get(
        organization_id=org_id,
        contract_id=contract.id,
    )

    assert updated.status == ContractStatus.COMPLETED
    assert updated.updated_at == fixed_time
    assert updated.updated_by_user_id == user_id


def test_set_contract_status_is_idempotent(
    contract_repo,
    uow,
):
    org_id = uuid4()

    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(CompanyBuilder().with_role(CompanyType.OWN).build())
        .with_status(ContractStatus.ACTIVE)
        .build()
    )

    contract_repo.add(contract)

    service = SetContractStatusService()

    cmd = SetContractStatusCommand(
        organization_id=org_id,
        contract_id=contract.id,
        actor_user_id=uuid4(),
        new_status=ContractStatus.ACTIVE,
    )

    service.execute(action=cmd, uow=uow)

    # status nie powinien się zmienić
    updated = contract_repo.get(
        organization_id=org_id,
        contract_id=contract.id,
    )

    assert updated.updated_at is None
    assert updated.updated_by_user_id is None


def test_set_contract_status_raises_when_not_found(
    uow,
):
    service = SetContractStatusService()

    cmd = SetContractStatusCommand(
        organization_id=uuid4(),
        contract_id=uuid4(),
        actor_user_id=uuid4(),
        new_status=ContractStatus.COMPLETED,
    )

    with pytest.raises(ValueError):
        service.execute(action=cmd, uow=uow)
