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



def _company(*, is_active: bool) -> Company:
    return Company(
        id=uuid4(),
        name="ABC",
        description=None,
        tax_number="1234567890",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.SUPPLIER,
        tags=set(),
        is_active=is_active,
    )


def test_deactivate_active_company():
    repo = InMemoryCompanyRepository()
    company = _company(is_active=True)
    repo.add(company)

    service = DeactivateCompanyService(repo)
    service.execute(company.id)

    updated = repo.get(company.id)
    assert updated is not None
    assert updated.is_active is False


def test_deactivate_is_idempotent():
    repo = InMemoryCompanyRepository()
    company = _company(is_active=False)
    repo.add(company)

    service = DeactivateCompanyService(repo)
    service.execute(company.id)

    updated = repo.get(company.id)
    assert updated.is_active is False


def test_deactivate_non_existing_company_raises():
    repo = InMemoryCompanyRepository()
    service = DeactivateCompanyService(repo)

    with pytest.raises(ValueError):
        service.execute(uuid4())



def test_activate_inactive_company():
    repo = InMemoryCompanyRepository()
    company = _company(is_active=False)
    repo.add(company)

    service = ActivateCompanyService(repo)
    service.execute(company.id)

    updated = repo.get(company.id)
    assert updated is not None
    assert updated.is_active is True


def test_activate_is_idempotent():
    repo = InMemoryCompanyRepository()
    company = _company(is_active=True)
    repo.add(company)

    service = ActivateCompanyService(repo)
    service.execute(company.id)

    updated = repo.get(company.id)
    assert updated.is_active is True


def test_activate_non_existing_company_raises():
    repo = InMemoryCompanyRepository()
    service = ActivateCompanyService(repo)

    with pytest.raises(ValueError):
        service.execute(uuid4())
