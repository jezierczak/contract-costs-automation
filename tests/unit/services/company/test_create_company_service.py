from uuid import uuid4
from datetime import datetime

from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.companies.dto.create_company_command import (
    CreateCounterpartyCompanyCommand,
    CreateOwnerCompanyCommand,
)
from contract_costs.model.company import CompanyType


def test_create_company_success(company_repo, create_system_contract, uow):


    fixed_id = uuid4()
    fixed_time = datetime(2024, 1, 1)

    service = CreateCompanyService(
        create_system_contract=create_system_contract,
        id_generator=lambda: fixed_id,
        clock=lambda: fixed_time,

    )

    org_id = uuid4()
    actor_id = uuid4()

    cmd = CreateCounterpartyCompanyCommand(
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

    company = service.execute(action=cmd, uow=uow)

    assert company.id == fixed_id
    assert company.tax_number == "1234563218"
    assert company.created_at == fixed_time
    assert company_repo.get(company.id, org_id) == company


import pytest


def test_duplicate_tax_number_in_same_org_raises(create_system_contract, uow):
    service = CreateCompanyService(create_system_contract=create_system_contract)

    org_id = uuid4()

    cmd = CreateCounterpartyCompanyCommand(
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

    service.execute(action=cmd, uow=uow)

    with pytest.raises(ValueError):
        service.execute(action=cmd, uow=uow)


def test_same_tax_number_allowed_in_different_org(create_system_contract, uow):
    service = CreateCompanyService(create_system_contract=create_system_contract)

    cmd1 = CreateCounterpartyCompanyCommand(
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

    cmd2 = CreateCounterpartyCompanyCommand(
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

    service.execute(action=cmd1, uow=uow)
    service.execute(action=cmd2, uow=uow)  # should not raise


def test_only_one_own_company_allowed(create_system_contract, uow):
    service = CreateCompanyService(create_system_contract=create_system_contract)

    org_id = uuid4()

    cmd = CreateOwnerCompanyCommand(
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

    service.execute(action=cmd, uow=uow)

    with pytest.raises(ValueError):
        service.execute(
            action=
            CreateOwnerCompanyCommand(
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
            ),
            uow=uow,
        )
