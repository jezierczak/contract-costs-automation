from datetime import datetime
from uuid import uuid4

from contract_costs.services.companies.activate_company_service import (
    ActivateCompanyService,
)
from contract_costs.services.companies.dto.activate_company_command import (
    ActivateCompanyCommand,
)
from tests.builders.company_builder import CompanyBuilder


def test_activate_company_success(company_repo):
    fixed_time = datetime(2024, 1, 1)

    service = ActivateCompanyService(
        company_repository=company_repo,
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

    cmd = ActivateCompanyCommand(
        organization_id=org_id,
        company_id=company.id,
        actor_user_id=actor_id,
    )

    service.execute(cmd)

    updated = company_repo.get(company.id, org_id)

    assert updated.is_active is True
    assert updated.updated_at == fixed_time
    assert updated.updated_by_user_id == actor_id


import pytest


def test_activate_company_not_exists_raises(company_repo):
    service = ActivateCompanyService(company_repo)

    cmd = ActivateCompanyCommand(
        organization_id=uuid4(),
        company_id=uuid4(),
        actor_user_id=uuid4(),
    )

    with pytest.raises(ValueError):
        service.execute(cmd)


def test_activate_company_is_idempotent(company_repo):
    service = ActivateCompanyService(company_repo)

    org_id = uuid4()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .is_active(True)
        .build()
    )

    company_repo.add(company)

    cmd = ActivateCompanyCommand(
        organization_id=org_id,
        company_id=company.id,
        actor_user_id=uuid4(),
    )

    service.execute(cmd)

    updated = company_repo.get(company.id, org_id)

    assert updated.is_active is True
    assert updated.updated_at == company.updated_at
    assert updated.updated_by_user_id == company.updated_by_user_id
