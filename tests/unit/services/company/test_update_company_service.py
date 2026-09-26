from datetime import datetime
from uuid import uuid4

from contract_costs.services.companies.update_company_service import UpdateCompanyService
from contract_costs.services.companies.dto.update_company_command import (
    UpdateCounterpartyCompanyCommand,
    UpdateOwnerCompanyCommand,
)
from contract_costs.model.company import CompanyType
from tests.builders.company_builder import CompanyBuilder


def test_update_company_success(company_repo, uow):
    fixed_time = datetime(2024, 1, 1)

    service = UpdateCompanyService(
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

    cmd = UpdateCounterpartyCompanyCommand(
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

    service.execute(action=cmd, uow=uow)

    updated = company_repo.get(company.id, org_id)

    assert updated.name == "New Name"
    assert updated.tax_number == "1234563218"
    assert updated.updated_at == fixed_time
    assert updated.updated_by_user_id == actor_id


import pytest


def test_update_company_not_exists_raises(uow):
    service = UpdateCompanyService()

    cmd = UpdateCounterpartyCompanyCommand(
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
        service.execute(action=cmd, uow=uow)


def test_update_company_duplicate_tax_number_raises(company_repo, uow):
    service = UpdateCompanyService()

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

    cmd = UpdateCounterpartyCompanyCommand(
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
        service.execute(action=cmd, uow=uow)


def test_update_company_keeps_tax_number_if_none(company_repo, uow):
    service = UpdateCompanyService()

    org_id = uuid4()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1234567890")
        .build()
    )

    company_repo.add(company)

    update_cmd_type = (
        UpdateOwnerCompanyCommand
        if company.role == CompanyType.OWN
        else UpdateCounterpartyCompanyCommand
    )

    cmd = update_cmd_type(
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

    service.execute(action=cmd, uow=uow)

    updated = company_repo.get(company.id, org_id)

    assert updated.tax_number == "1234567890"


def _numbering_cmd(company, org_id, **kwargs):
    return UpdateCounterpartyCompanyCommand(
        organization_id=org_id,
        company_id=company.id,
        actor_user_id=uuid4(),
        name=company.name,
        description=None,
        tax_number=None,
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.SUPPLIER,
        tags=None,
        **kwargs,
    )


def test_update_company_sets_reference_numbering_mode_only_when_requested(company_repo, uow):
    from contract_costs.model.company import ReferenceNumberingMode

    service = UpdateCompanyService()
    org_id = uuid4()
    company = CompanyBuilder().with_organization_id(org_id).with_tax_number("1234567890").build()
    company_repo.add(company)

    service.execute(
        action=_numbering_cmd(
            company, org_id,
            set_reference_numbering_mode=True,
            reference_numbering_mode=ReferenceNumberingMode.YEARLY,
        ),
        uow=uow,
    )
    assert company_repo.get(company.id, org_id).reference_numbering_mode == ReferenceNumberingMode.YEARLY

    # aktualizacja bez flagi (import z Excela, CLI) nie kasuje ustawienia
    service.execute(action=_numbering_cmd(company, org_id), uow=uow)
    assert company_repo.get(company.id, org_id).reference_numbering_mode == ReferenceNumberingMode.YEARLY

    # jawne wyczyszczenie z formularza → numer ręczny
    service.execute(
        action=_numbering_cmd(company, org_id, set_reference_numbering_mode=True, reference_numbering_mode=None),
        uow=uow,
    )
    assert company_repo.get(company.id, org_id).reference_numbering_mode is None
