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
        tax_number=kwargs.get("tax_number"),
        own_only=kwargs.get("own_only", False),
        role=kwargs.get("role"),
        include_inactive=kwargs.get("include_inactive", False),
        search=kwargs.get("search"),
    )


# ============================================================
# TESTS
# ============================================================


def test_returns_empty_when_no_companies(company_repo):
    service = CompanyQueryService(company_repo)
    org_id = new_uuid()

    result = service.execute(build_query(org_id))

    assert result == []


def test_filter_by_tax_number(company_repo):
    service = CompanyQueryService(company_repo)
    org_id = new_uuid()

    c = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("999")
        .build()
    )

    company_repo.add(c)

    result = service.execute(
        build_query(org_id, tax_number="999")
    )

    assert len(result) == 1
    assert result[0].tax_number == "999"


def test_own_only_filter(company_repo):
    service = CompanyQueryService(company_repo)
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

    result = service.execute(
        build_query(org_id, own_only=True)
    )

    assert len(result) == 1
    assert result[0].role == CompanyType.OWN


def test_role_filter(company_repo):
    service = CompanyQueryService(company_repo)
    org_id = new_uuid()

    supplier = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .build()
    )

    company_repo.add(supplier)

    result = service.execute(
        build_query(org_id, role=CompanyType.SUPPLIER)
    )

    assert len(result) == 1
    assert result[0].role == CompanyType.SUPPLIER


def test_excludes_inactive_by_default(company_repo):
    service = CompanyQueryService(company_repo)
    org_id = new_uuid()

    inactive = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .is_active(False)
        .build()
    )

    company_repo.add(inactive)

    result = service.execute(build_query(org_id))

    assert result == []


def test_include_inactive(company_repo):
    service = CompanyQueryService(company_repo)
    org_id = new_uuid()

    inactive = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .is_active(False)
        .build()
    )

    company_repo.add(inactive)

    result = service.execute(
        build_query(org_id, include_inactive=True)
    )

    assert len(result) == 1
    assert result[0].is_active is False


def test_search_matches_name_and_city(company_repo):
    service = CompanyQueryService(company_repo)
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("Mega Company")
        .with_address(city="Krakow")
        .build()
    )

    company_repo.add(company)

    result = service.execute(
        build_query(org_id, search="mega")
    )

    assert len(result) == 1

    result = service.execute(
        build_query(org_id, search="krak")
    )

    assert len(result) == 1


def test_search_is_case_insensitive(company_repo):
    service = CompanyQueryService(company_repo)
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("SuperCompany")
        .build()
    )

    company_repo.add(company)

    result = service.execute(
        build_query(org_id, search="super")
    )

    assert len(result) == 1


def test_returns_dto_with_quality_score(company_repo):
    service = CompanyQueryService(company_repo)
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .build()
    )

    company_repo.add(company)

    result = service.execute(build_query(org_id))

    assert len(result) == 1
    assert isinstance(result[0].quality_score, (int, float))
