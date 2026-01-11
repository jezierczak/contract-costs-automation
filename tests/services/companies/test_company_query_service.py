import pytest

from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.query.company_query_service import (
    CompanyQueryService,
)
from contract_costs.services.companies.query.dto.company_query import CompanyQuery


@pytest.fixture
def repo():
    return InMemoryCompanyRepository()


@pytest.fixture
def query_service(repo):
    return CompanyQueryService(company_repository=repo)

from uuid import uuid4
from contract_costs.model.company import Company, CompanyType


def company(
    *,
    name="Company",
    tax_number="123",
    role: CompanyType = CompanyType.CLIENT,
    is_active=True,
    description=None,
):
    return Company(
        id=uuid4(),
        name=name,
        description=description,
        tax_number=tax_number,
        address=None,
        contact=None,
        bank_account=None,
        role=role,
        tags=set(),
        is_active=is_active,
    )


def test_query_returns_only_active_by_default(repo, query_service):
    repo.add(company(is_active=True))
    repo.add(company(is_active=False))

    result = query_service.list_companies(CompanyQuery())

    assert len(result) == 1
    assert result[0].is_active is True

def test_query_include_inactive(repo, query_service):
    repo.add(company(is_active=True))
    repo.add(company(is_active=False))

    result = query_service.list_companies(
        CompanyQuery(include_inactive=True)
    )

    assert len(result) == 2


def test_query_own_only(repo, query_service):
    repo.add(company(role=CompanyType.OWN))
    repo.add(company(role=CompanyType.CLIENT))

    result = query_service.list_companies(
        CompanyQuery(own_only=True)
    )

    assert len(result) == 1
    assert result[0].role == CompanyType.OWN


def test_query_tax_number_strict(repo, query_service):
    repo.add(company(tax_number="123"))
    repo.add(company(tax_number="456"))

    result = query_service.list_companies(
        CompanyQuery(tax_number="123")
    )

    assert len(result) == 1
    assert result[0].tax_number == "123"


def test_query_role_filter(repo, query_service):
    repo.add(company(role=CompanyType.SUPPLIER))
    repo.add(company(role=CompanyType.CLIENT))

    result = query_service.list_companies(
        CompanyQuery(role=CompanyType.SUPPLIER)
    )

    assert len(result) == 1
    assert result[0].role == CompanyType.SUPPLIER


def test_query_search_in_name(repo, query_service):
    repo.add(company(name="ABC Sp. z o.o."))
    repo.add(company(name="XYZ Company"))

    result = query_service.list_companies(
        CompanyQuery(search="abc")
    )

    assert len(result) == 1
    assert "ABC" in result[0].name


def test_query_search_in_description(repo, query_service):
    repo.add(company(description="Main supplier"))
    repo.add(company(description="Other"))

    result = query_service.list_companies(
        CompanyQuery(search="supplier")
    )

    assert len(result) == 1


def test_query_combined_filters(repo, query_service):
    repo.add(company(
        name="Mine",
        role=CompanyType.OWN,
        is_active=True,
    ))
    repo.add(company(
        name="Mine",
        role=CompanyType.CLIENT,
        is_active=True,
    ))
    repo.add(company(
        name="Mine",
        role=CompanyType.OWN,
        is_active=False,
    ))

    result = query_service.list_companies(
        CompanyQuery(
            own_only=True,
            include_inactive=False,
            search="mine",
        )
    )

    assert len(result) == 1
    assert result[0].role == CompanyType.OWN
    assert result[0].is_active is True
