from uuid import uuid4

import pytest

from contract_costs.model.company import Company, CompanyType
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.deactivate_company_service import (
    DeactivateCompanyService,
)
from contract_costs.services.companies.activate_company_service import (
    ActivateCompanyService,
)
from contract_costs.services.companies.dto.activate_company_command import BaseActivateCompanyCommand
from datetime import datetime
from uuid import uuid4

from contract_costs.services.companies.dto.deactivate_company_command import BaseDeactivateCompanyCommand

NOW = datetime(2024, 1, 1)

TEST_ORG_ID = uuid4()
TEST_USER_ID = uuid4()

def make_company(*, is_active: bool) -> Company:
    return Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="ABC",
        description=None,
        tax_number="1234567890",

        address=None,
        contact=None,
        bank_account=None,

        role=CompanyType.SUPPLIER,
        tags=set(),
        is_active=is_active,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )


def test_deactivate_active_company():
    repo = InMemoryCompanyRepository()
    company = make_company(is_active=True)
    repo.add(company)

    service = DeactivateCompanyService(repo)

    cmd = BaseDeactivateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=company.id,
        actor_user_id=TEST_USER_ID,
    )

    service.execute(cmd)

    updated = repo.get(company.id,TEST_ORG_ID)
    assert updated.is_active is False


def test_deactivate_is_idempotent():
    repo = InMemoryCompanyRepository()
    company = make_company(is_active=False)
    repo.add(company)

    service = DeactivateCompanyService(repo)

    cmd = BaseDeactivateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=company.id,
        actor_user_id=TEST_USER_ID,
    )

    service.execute(cmd)

    updated = repo.get(company.id,TEST_ORG_ID)
    assert updated.is_active is False


def test_deactivate_non_existing_company_raises():
    repo = InMemoryCompanyRepository()
    service = DeactivateCompanyService(repo)

    cmd = BaseDeactivateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=uuid4(),
        actor_user_id=TEST_USER_ID,
    )

    with pytest.raises(ValueError, match="Company does not exist"):
        service.execute(cmd)



def test_activate_inactive_company():
    repo = InMemoryCompanyRepository()
    company = make_company(is_active=False)
    repo.add(company)

    service = ActivateCompanyService(repo)

    cmd = BaseActivateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=company.id,
        actor_user_id=TEST_USER_ID,
    )

    service.execute(cmd)

    updated = repo.get(company.id,TEST_ORG_ID)
    assert updated.is_active is True


def test_activate_is_idempotent():
    repo = InMemoryCompanyRepository()
    company = make_company(is_active=True)
    repo.add(company)

    service = ActivateCompanyService(repo)

    cmd = BaseActivateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=company.id,
        actor_user_id=TEST_USER_ID,
    )

    service.execute(cmd)

    updated = repo.get(company.id,TEST_ORG_ID)
    assert updated.is_active is True


def test_activate_non_existing_company_raises():
    repo = InMemoryCompanyRepository()
    service = ActivateCompanyService(repo)

    cmd = BaseActivateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=uuid4(),
        actor_user_id=TEST_USER_ID,
    )

    with pytest.raises(ValueError, match="Company does not exist"):
        service.execute(cmd)
