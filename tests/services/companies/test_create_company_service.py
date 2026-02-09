import pytest
from uuid import UUID, uuid4
from datetime import datetime

from contract_costs.model.company import CompanyType
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.companies.dto.create_company_command import CreateCompanyCommand


TEST_ORG_ID = uuid4()
TEST_USER_ID = uuid4()
NOW = datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def company_repo():
    return InMemoryCompanyRepository()


@pytest.fixture
def service(company_repo):
    return CreateCompanyService(
        company_repository=company_repo,
        clock=lambda: NOW,
    )

def test_create_company_success(service, company_repo):
    cmd = CreateCompanyCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        name="Test Company",
        tax_number="PL 123-456-78-90",
        role=CompanyType.OWN,
    )

    company = service.execute(cmd)

    assert company.id is not None
    assert isinstance(company.id, UUID)

    assert company.organization_id == TEST_ORG_ID
    assert company.name == "Test Company"
    assert company.tax_number == "1234567890"   # 🔥 normalizacja
    assert company.role == CompanyType.OWN
    assert company.is_active is True
    assert company.tags == set()

    assert company.created_at == NOW
    assert company.created_by_user_id == TEST_USER_ID
    assert company.updated_at is None
    assert company.updated_by_user_id is None

    # faktycznie zapisane w repo (ORG-SCOPED)
    stored = company_repo.get_by_tax_number(
        tax_number="1234567890",
        organization_id=TEST_ORG_ID,
    )

    assert stored is not None
    assert stored.id == company.id


def test_create_company_with_optional_fields(service):
    cmd = CreateCompanyCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        name="Full Company",
        tax_number="1234567890",
        role=CompanyType.CLIENT,
        description="Some description",
        tags={"vip", "partner"},
    )

    company = service.execute(cmd)

    assert company.description == "Some description"
    assert company.tags == {"vip", "partner"}
    assert company.role == CompanyType.CLIENT


def test_create_company_duplicate_tax_number_raises(service):
    first = CreateCompanyCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        name="First",
        tax_number="1234567890",
        role=CompanyType.OWN,
    )

    service.execute(first)

    second = CreateCompanyCommand(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        name="Second",
        tax_number="PL 1234567890",  # ta sama firma po normalizacji
        role=CompanyType.OWN,
    )

    with pytest.raises(ValueError, match="Company with this tax number already exists"):
        service.execute(second)

