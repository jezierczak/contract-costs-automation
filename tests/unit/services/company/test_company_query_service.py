import pytest

from contract_costs.common.ids import new_uuid
from contract_costs.model.company import CompanyType
from contract_costs.services.companies.query.company_query_service import (
    CompanyQueryService,
)
from contract_costs.services.companies.query.dto.company_query import CompanyQuery
from tests.builders.company_builder import CompanyBuilder


# ============================================================
# HELPERS
# ============================================================

def build_query(org_id, **kwargs):
    return CompanyQuery(
        organization_id=org_id,
        actor_user_id=kwargs.get("actor_user_id", new_uuid()),
        tax_number=kwargs.get("tax_number"),
        own_only=kwargs.get("own_only", False),
        role=kwargs.get("role"),
        include_inactive=kwargs.get("include_inactive", False),
        search=kwargs.get("search"),
    )


# ============================================================
# TESTS
# ============================================================


def test_returns_empty_when_no_companies(uow):
    service = CompanyQueryService()
    org_id = new_uuid()

    result = service.execute(action=build_query(org_id), uow=uow)

    assert result == []


def test_filter_by_tax_number(company_repo, uow):
    service = CompanyQueryService()
    org_id = new_uuid()

    c = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("999")
        .build()
    )

    company_repo.add(c)

    result = service.execute(action=build_query(org_id, tax_number="999"), uow=uow)

    assert len(result) == 1
    assert result[0].tax_number == "999"


def test_own_only_filter(company_repo, uow):
    service = CompanyQueryService()
    org_id = new_uuid()

    own = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .build()
    )

    supplier = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .build()
    )

    company_repo.add(own)
    company_repo.add(supplier)

    result = service.execute(action=build_query(org_id, own_only=True), uow=uow)

    assert len(result) == 1
    assert result[0].role == CompanyType.OWN


def test_role_filter(company_repo, uow):
    service = CompanyQueryService()
    org_id = new_uuid()

    supplier = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .build()
    )

    company_repo.add(supplier)

    result = service.execute(action=build_query(org_id, role=CompanyType.SUPPLIER), uow=uow)

    assert len(result) == 1
    assert result[0].role == CompanyType.SUPPLIER


def test_excludes_inactive_by_default(company_repo, uow):
    service = CompanyQueryService()
    org_id = new_uuid()

    inactive = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .is_active(False)
        .build()
    )

    company_repo.add(inactive)

    result = service.execute(action=build_query(org_id), uow=uow)

    assert result == []


def test_include_inactive(company_repo, uow):
    service = CompanyQueryService()
    org_id = new_uuid()

    inactive = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .is_active(False)
        .build()
    )

    company_repo.add(inactive)

    result = service.execute(action=build_query(org_id, include_inactive=True), uow=uow)

    assert len(result) == 1
    assert result[0].is_active is False


def test_search_matches_name_and_city(company_repo, uow):
    service = CompanyQueryService()
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("Mega Company")
        .with_address(city="Krakow")
        .build()
    )

    company_repo.add(company)

    result = service.execute(action=build_query(org_id, search="mega"), uow=uow)

    assert len(result) == 1

    result = service.execute(action=build_query(org_id, search="krak"), uow=uow)

    assert len(result) == 1


def test_search_is_case_insensitive(company_repo, uow):
    service = CompanyQueryService()
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("SuperCompany")
        .build()
    )

    company_repo.add(company)

    result = service.execute(action=build_query(org_id, search="super"), uow=uow)

    assert len(result) == 1


def test_returns_dto_with_quality_score(company_repo, uow):
    service = CompanyQueryService()
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .build()
    )

    company_repo.add(company)

    result = service.execute(action=build_query(org_id), uow=uow)

    assert len(result) == 1
    assert isinstance(result[0].quality_score, (int, float))


def test_to_verify_only_filter(company_repo, uow):
    from contract_costs.model.company import CompanyVerificationStatus

    service = CompanyQueryService()
    org_id = new_uuid()
    verified = CompanyBuilder().with_organization_id(org_id).with_tax_number("5261009959").build()
    to_verify = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("TMP-abcd1234")
        .with_verification_status(CompanyVerificationStatus.TO_VERIFY)
        .build()
    )
    company_repo.add(verified)
    company_repo.add(to_verify)

    result = service.execute(
        action=CompanyQuery(organization_id=org_id, actor_user_id=new_uuid(), to_verify_only=True),
        uow=uow,
    )

    assert [dto.id for dto in result] == [to_verify.id]
    assert result[0].verification_status == CompanyVerificationStatus.TO_VERIFY
