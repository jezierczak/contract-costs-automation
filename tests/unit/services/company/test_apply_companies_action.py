import pytest
from uuid import uuid4

from contract_costs.services.companies.apply.apply_companies_from_excel_service import ApplyCompaniesFromExcelService
from contract_costs.services.companies.apply.command import (
    ApplyCompaniesCommand,
    ApplyCompanyCommand,
    CompanyActionType,
)
from contract_costs.model.company import CompanyType
from tests.builders.company_builder import CompanyBuilder

TEST_ORG_ID = uuid4()
TEST_USER_ID = uuid4()


def test_apply_create_creates_company(
    company_repo,
    create_company_service,
    update_service,
    activate_service,
    deactivate_service,
    uow,
):
    action = ApplyCompaniesFromExcelService(
        create_company_service=create_company_service,
        update_company_service=update_service,
        activate_company_service=activate_service,
        deactivate_company_service=deactivate_service,
    )

    cmd = ApplyCompanyCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        apply_action_type=CompanyActionType.CREATE,
        company_id=None,
        name="ACME",
        tax_number="1234563218",
        role=CompanyType.SUPPLIER,
        description=None,
        address_street="Main 1",
        address_city="Krakow",
        address_zip_code="30-001",
        address_country="PL",
        phone_number=None,
        email=None,
        bank_account_number=None,
        bank_account_country_code=None,
        tags=set(),
    )

    apply_cmd = ApplyCompaniesCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        commands=[cmd],
    )

    action.execute(action=apply_cmd, uow=uow)

    companies = company_repo.list_all(TEST_ORG_ID)
    assert len(companies) == 1
    assert companies[0].name == "ACME"


def test_apply_update_updates_company(
    company_repo,
    create_company_service,
    update_service,
    activate_service,
    deactivate_service,
    uow,
):

    existing = CompanyBuilder().with_organization_id(TEST_ORG_ID).with_name("OLD").build()
    company_repo.add(existing)

    action = ApplyCompaniesFromExcelService(
        create_company_service=create_company_service,
        update_company_service=update_service,
        activate_company_service=activate_service,
        deactivate_company_service=deactivate_service,
    )

    cmd = ApplyCompanyCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        apply_action_type=CompanyActionType.UPDATE,
        company_id=existing.id,
        name="NEW",
        tax_number=existing.tax_number,
        role=existing.role,
        description=None,
        address_street=None,
        address_city=None,
        address_zip_code=None,
        address_country=None,
        phone_number=None,
        email=None,
        bank_account_number=None,
        bank_account_country_code=None,
        tags=set(),
    )

    apply_cmd = ApplyCompaniesCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        commands=[cmd],
    )

    action.execute(action=apply_cmd, uow=uow)

    updated = company_repo.get(existing.id, TEST_ORG_ID)
    assert updated.name == "NEW"

def test_apply_deactivate(
    company_repo,
    create_company_service,
    update_service,
    activate_service,
    deactivate_service,
    uow,
):

    company = CompanyBuilder().with_organization_id(org_id=TEST_ORG_ID).is_active(is_active=True).build()
    company_repo.add(company)

    action = ApplyCompaniesFromExcelService(
        create_company_service=create_company_service,
        update_company_service=update_service,
        activate_company_service=activate_service,
        deactivate_company_service=deactivate_service,
    )

    cmd = ApplyCompanyCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        apply_action_type=CompanyActionType.DEACTIVATE,
        company_id=company.id,
        name=company.name,
        tax_number=company.tax_number,
        role=company.role,
        description=None,
        address_street=None,
        address_city=None,
        address_zip_code=None,
        address_country=None,
        phone_number=None,
        email=None,
        bank_account_number=None,
        bank_account_country_code=None,
        tags=set(),
    )

    apply_cmd = ApplyCompaniesCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        commands=[cmd],
    )

    action.execute(action=apply_cmd, uow=uow)

    updated = company_repo.get(company.id, TEST_ORG_ID)
    assert updated.is_active is False
