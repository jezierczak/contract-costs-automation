from datetime import datetime
from uuid import uuid4

from contract_costs.services.companies.activate_company_service import (
    ActivateCompanyService,
)
from contract_costs.services.companies.dto.activate_company_command import (
    BaseActivateCompanyCommand,
)
from tests.builders.company_builder import CompanyBuilder


def test_activate_company_success(company_repo, uow):
    fixed_time = datetime(2024, 1, 1)

    service = ActivateCompanyService(
        clock=lambda: fixed_time,
    )

    org_id = uuid4()
    actor_id = uuid4()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .is_active(False)
        .build()
    )

    company_repo.add(company)

    cmd = BaseActivateCompanyCommand(
        organization_id=org_id,
        company_id=company.id,
        actor_user_id=actor_id,
    )

    service.execute(action=cmd, uow=uow)

    updated = company_repo.get(company.id, org_id)

    assert updated.is_active is True
    assert updated.updated_at == fixed_time
    assert updated.updated_by_user_id == actor_id


import pytest


def test_activate_company_not_exists_raises(uow):
    service = ActivateCompanyService()

    cmd = BaseActivateCompanyCommand(
        organization_id=uuid4(),
        company_id=uuid4(),
        actor_user_id=uuid4(),
    )

    with pytest.raises(ValueError):
        service.execute(action=cmd, uow=uow)


def test_activate_company_is_idempotent(company_repo, uow):
    service = ActivateCompanyService()

    org_id = uuid4()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .is_active(True)
        .build()
    )

    company_repo.add(company)

    cmd = BaseActivateCompanyCommand(
        organization_id=org_id,
        company_id=company.id,
        actor_user_id=uuid4(),
    )

    service.execute(action=cmd, uow=uow)

    updated = company_repo.get(company.id, org_id)

    assert updated.is_active is True
    assert updated.updated_at == company.updated_at
    assert updated.updated_by_user_id == company.updated_by_user_id
