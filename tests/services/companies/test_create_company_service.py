import pytest
from uuid import UUID

from contract_costs.model.company import CompanyType
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.create_company_service import CreateCompanyService


@pytest.fixture
def company_repo():
    return InMemoryCompanyRepository()


@pytest.fixture
def service(company_repo):
    return CreateCompanyService(company_repo)


def test_create_company_success(service, company_repo):
    company = service.execute(
        name="Test Company",
        tax_number="PL 123-456-78-90",
        role=CompanyType.OWN,
    )

    assert company.id is not None
    assert isinstance(company.id, UUID)
    assert company.name == "Test Company"
    assert company.tax_number == "1234567890"   # 🔥 normalizacja
    assert company.role == CompanyType.OWN
    assert company.is_active is True
    assert company.tags == set()

    # faktycznie zapisane w repo
    stored = company_repo.get_by_tax_number("1234567890")
    assert stored is not None
    assert stored.id == company.id


def test_create_company_with_optional_fields(service):
    company = service.execute(
        name="Full Company",
        tax_number="1234567890",
        role=CompanyType.CLIENT,
        description="Some description",
        tags={"vip", "partner"},
    )

    assert company.description == "Some description"
    assert company.tags == {"vip", "partner"}
    assert company.role == CompanyType.CLIENT


def test_create_company_duplicate_tax_number_raises(service):
    service.execute(
        name="First",
        tax_number="1234567890",
        role=CompanyType.OWN,
    )

    with pytest.raises(ValueError, match="Company with this tax number already exists"):
        service.execute(
            name="Second",
            tax_number="PL 1234567890",  # ta sama firma po normalizacji
            role=CompanyType.OWN,
        )
