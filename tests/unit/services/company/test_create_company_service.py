from uuid import uuid4
from datetime import datetime

from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.companies.dto.create_company_command import CreateCompanyCommand
from contract_costs.model.company import CompanyType


def test_create_company_success():
    repo = InMemoryCompanyRepository()

    fixed_id = uuid4()
    fixed_time = datetime(2024, 1, 1)

    service = CreateCompanyService(
        company_repository=repo,
        id_generator=lambda: fixed_id,
        clock=lambda: fixed_time,
    )

    org_id = uuid4()
    actor_id = uuid4()

    cmd = CreateCompanyCommand(
        organization_id=org_id,
        actor_user_id=actor_id,
        name="Test",
        description=None,
        tax_number="PL 123-456-32-18",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.SUPPLIER,
        tags=None,
    )

    company = service.execute(cmd)

    assert company.id == fixed_id
    assert company.tax_number == "1234563218"
    assert company.created_at == fixed_time
    assert repo.get(company.id, org_id) == company


import pytest


def test_duplicate_tax_number_in_same_org_raises(company_repo):
    repo = company_repo
    service = CreateCompanyService(repo)

    org_id = uuid4()

    cmd = CreateCompanyCommand(
        organization_id=org_id,
        actor_user_id=uuid4(),
        name="A",
        description=None,
        tax_number="1234567890",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.SUPPLIER,
        tags=None,
    )

    service.execute(cmd)

    with pytest.raises(ValueError):
        service.execute(cmd)


def test_same_tax_number_allowed_in_different_org(company_repo):
    repo = company_repo
    service = CreateCompanyService(repo)

    cmd1 = CreateCompanyCommand(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        name="A",
        description=None,
        tax_number="1234567890",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.SUPPLIER,
        tags=None,
    )

    cmd2 = CreateCompanyCommand(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        name="B",
        description=None,
        tax_number="1234567890",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.SUPPLIER,
        tags=None,
    )

    service.execute(cmd1)
    service.execute(cmd2)  # should not raise


def test_only_one_own_company_allowed(company_repo):
    repo = company_repo
    service = CreateCompanyService(repo)

    org_id = uuid4()

    cmd = CreateCompanyCommand(
        organization_id=org_id,
        actor_user_id=uuid4(),
        name="Owner",
        description=None,
        tax_number="1234567890",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.OWN,
        tags=None,
    )

    service.execute(cmd)

    with pytest.raises(ValueError):
        service.execute(
            CreateCompanyCommand(
                organization_id=org_id,
                actor_user_id=uuid4(),
                name="Owner2",
                description=None,
                tax_number="9876543210",
                address=None,
                contact=None,
                bank_account=None,
                role=CompanyType.OWN,
                tags=None,
            )
        )
