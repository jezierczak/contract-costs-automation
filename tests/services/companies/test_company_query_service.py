import pytest
from uuid import uuid4
from datetime import datetime

from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.query.company_query_service import (
    CompanyQueryService,
)
from contract_costs.services.companies.query.dto.company_query import CompanyQuery


TEST_ORG_ID = uuid4()
OTHER_ORG_ID = uuid4()
TEST_USER_ID = uuid4()
NOW = datetime(2024, 1, 1, 12, 0, 0)

@pytest.fixture
def repo():
    return InMemoryCompanyRepository()


@pytest.fixture
def query_service(repo):
    return CompanyQueryService(company_repository=repo)

from uuid import uuid4
from contract_costs.model.company import Company, CompanyType



def make_company(
    *,
    name="Company",
    tax_number="123",
    role: CompanyType = CompanyType.CLIENT,
    is_active=True,
    description=None,
    organization_id=TEST_ORG_ID,
):
    return Company(
        id=uuid4(),
        organization_id=organization_id,

        name=name,
        description=description,
        tax_number=tax_number,

        address=None,
        contact=None,
        bank_account=None,

        role=role,
        tags=set(),
        is_active=is_active,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )


def test_query_returns_only_active_by_default(repo, query_service):
    repo.add(make_company(is_active=True))
    repo.add(make_company(is_active=False))

    result = query_service.list_companies(
        CompanyQuery(organization_id=TEST_ORG_ID)
    )

    assert len(result) == 1
    assert result[0].is_active is True


def test_query_include_inactive(repo, query_service):
    repo.add(make_company(is_active=True))
    repo.add(make_company(is_active=False))

    result = query_service.list_companies(
        CompanyQuery(
            organization_id=TEST_ORG_ID,
            include_inactive=True,
        )
    )

    assert len(result) == 2


def test_query_own_only(repo, query_service):
    repo.add(make_company(role=CompanyType.OWN))
    repo.add(make_company(role=CompanyType.CLIENT))

    result = query_service.list_companies(
        CompanyQuery(
            organization_id=TEST_ORG_ID,
            own_only=True,
        )
    )

    assert len(result) == 1
    assert result[0].role == CompanyType.OWN


def test_query_tax_number_strict(repo, query_service):
    repo.add(make_company(tax_number="123"))
    repo.add(make_company(tax_number="456"))

    result = query_service.list_companies(
        CompanyQuery(
            organization_id=TEST_ORG_ID,
            tax_number="123",
        )
    )

    assert len(result) == 1
    assert result[0].tax_number == "123"


def test_query_role_filter(repo, query_service):
    repo.add(make_company(role=CompanyType.SUPPLIER))
    repo.add(make_company(role=CompanyType.CLIENT))

    result = query_service.list_companies(
        CompanyQuery(
            organization_id=TEST_ORG_ID,
            role=CompanyType.SUPPLIER,
        )
    )

    assert len(result) == 1
    assert result[0].role == CompanyType.SUPPLIER



def test_query_search_in_name(repo, query_service):
    repo.add(make_company(name="ABC Sp. z o.o."))
    repo.add(make_company(name="XYZ Company"))

    result = query_service.list_companies(
        CompanyQuery(
            organization_id=TEST_ORG_ID,
            search="abc",
        )
    )

    assert len(result) == 1
    assert "ABC" in result[0].name


def test_query_search_in_description(repo, query_service):
    repo.add(make_company(description="Main supplier"))
    repo.add(make_company(description="Other"))

    result = query_service.list_companies(
        CompanyQuery(
            organization_id=TEST_ORG_ID,
            search="supplier",
        )
    )

    assert len(result) == 1



def test_query_combined_filters(repo, query_service):
    repo.add(make_company(
        name="Mine",
        role=CompanyType.OWN,
        is_active=True,
    ))
    repo.add(make_company(
        name="Mine",
        role=CompanyType.CLIENT,
        is_active=True,
    ))
    repo.add(make_company(
        name="Mine",
        role=CompanyType.OWN,
        is_active=False,
    ))

    result = query_service.list_companies(
        CompanyQuery(
            organization_id=TEST_ORG_ID,
            own_only=True,
            include_inactive=False,
            search="mine",
        )
    )

    assert len(result) == 1
    assert result[0].role == CompanyType.OWN
    assert result[0].is_active is True


def test_query_is_scoped_to_organization(repo, query_service):
    repo.add(make_company(name="Org A", organization_id=TEST_ORG_ID))
    repo.add(make_company(name="Org B", organization_id=OTHER_ORG_ID))

    result = query_service.list_companies(
        CompanyQuery(organization_id=TEST_ORG_ID)
    )

    assert len(result) == 1
    assert result[0].name == "Org A"

