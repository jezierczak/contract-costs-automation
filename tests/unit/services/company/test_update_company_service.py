from datetime import datetime
from uuid import uuid4

from contract_costs.services.companies.update_company_service import UpdateCompanyService
from contract_costs.services.companies.dto.update_company_command import UpdateCompanyCommand
from contract_costs.model.company import CompanyType
from tests.builders.company_builder import CompanyBuilder


def test_update_company_success(company_repo):
    fixed_time = datetime(2024, 1, 1)

    service = UpdateCompanyService(
        company_repository=company_repo,
        clock=lambda: fixed_time,
    )

    org_id = uuid4()
    actor_id = uuid4()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("Old Name")
        .with_tax_number("1234567890")
        .build()
    )

    company_repo.add(company)

    cmd = UpdateCompanyCommand(
        organization_id=org_id,
        company_id=company.id,
        actor_user_id=actor_id,
        name="New Name",
        description="Desc",
        tax_number="PL 123-456-32-18",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.SUPPLIER,
        tags={"a", "b"},
    )

    service.execute(cmd)

    updated = company_repo.get(company.id, org_id)

    assert updated.name == "New Name"
    assert updated.tax_number == "1234563218"
    assert updated.updated_at == fixed_time
    assert updated.updated_by_user_id == actor_id


import pytest


def test_update_company_not_exists_raises(company_repo):
    service = UpdateCompanyService(company_repo)

    cmd = UpdateCompanyCommand(
        organization_id=uuid4(),
        company_id=uuid4(),
        actor_user_id=uuid4(),
        name="X",
        description=None,
        tax_number=None,
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.SUPPLIER,
        tags=None,
    )

    with pytest.raises(ValueError):
        service.execute(cmd)


def test_update_company_duplicate_tax_number_raises(company_repo):
    service = UpdateCompanyService(company_repo)

    org_id = uuid4()

    c1 = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1111111111")
        .build()
    )

    c2 = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("2222222222")
        .build()
    )

    company_repo.add(c1)
    company_repo.add(c2)

    cmd = UpdateCompanyCommand(
        organization_id=org_id,
        company_id=c2.id,
        actor_user_id=uuid4(),
        name=c2.name,
        description=None,
        tax_number="1111111111",  # duplicate
        address=None,
        contact=None,
        bank_account=None,
        role=c2.role,
        tags=None,
    )

    import pytest
    with pytest.raises(ValueError):
        service.execute(cmd)


def test_update_company_keeps_tax_number_if_none(company_repo):
    service = UpdateCompanyService(company_repo)

    org_id = uuid4()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1234567890")
        .build()
    )

    company_repo.add(company)

    cmd = UpdateCompanyCommand(
        organization_id=org_id,
        company_id=company.id,
        actor_user_id=uuid4(),
        name=company.name,
        description=None,
        tax_number=None,
        address=None,
        contact=None,
        bank_account=None,
        role=company.role,
        tags=None,
    )

    service.execute(cmd)

    updated = company_repo.get(company.id, org_id)

    assert updated.tax_number == "1234567890"
