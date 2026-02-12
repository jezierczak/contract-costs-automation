import pytest
from uuid import uuid4
from datetime import datetime

from contract_costs.model.company import (
    Company,
    CompanyType,
    Address,
    Contact,
    BankAccount,
)
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.update_company_service import UpdateCompanyService
from contract_costs.services.companies.dto.update_company_command import UpdateCompanyCommand


TEST_ORG_ID = uuid4()
TEST_USER_ID = uuid4()
NOW = datetime(2024, 1, 1)


# =====================
# FIXTURES
# =====================

@pytest.fixture
def company_repo():
    return InMemoryCompanyRepository()


@pytest.fixture
def service(company_repo):
    return UpdateCompanyService(company_repo)


@pytest.fixture
def existing_company(company_repo):
    company = Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="Old name",
        tax_number="1234567890",
        description="Old desc",

        address=None,
        contact=None,
        bank_account=None,

        role=CompanyType.OWN,
        tags={"old"},
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )
    company_repo.add(company)
    return company


@pytest.fixture
def valid_address():
    return Address(
        street="Main",
        city="Warsaw",
        zip_code="00-001",
        country="PL",
    )


@pytest.fixture
def new_contact():
    return Contact(
        email="test@example.com",
        phone_number="123456789",
    )


@pytest.fixture
def new_bank_account():
    return BankAccount(
        account_number="12345678901234567890123456",
        country_code="PL",
    )


# =====================
# TESTS
# =====================

def test_update_company_not_existing_raises(service, valid_address):
    cmd = UpdateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=uuid4(),
        actor_user_id=TEST_USER_ID,

        name="X",
        role=CompanyType.CLIENT,
        address=valid_address,
        contact=None,
        description=None,
        tax_number=None,
        bank_account=None,
        tags=None,
    )

    with pytest.raises(ValueError, match="Company does not exist"):
        service.execute(cmd)


def test_update_company_updates_all_fields(
    service,
    company_repo,
    existing_company,
    valid_address,
    new_contact,
    new_bank_account,
):
    cmd = UpdateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=existing_company.id,
        actor_user_id=TEST_USER_ID,

        name="New name",
        role=CompanyType.CLIENT,
        address=valid_address,
        contact=new_contact,
        description="New desc",
        tax_number="9999999999",
        bank_account=new_bank_account,
        tags={"new", "vip"},
    )

    service.execute(cmd)

    updated = company_repo.get(existing_company.id, TEST_ORG_ID)

    assert updated.name == "New name"
    assert updated.tax_number == "9999999999"
    assert updated.address == valid_address
    assert updated.contact == new_contact
    assert updated.bank_account == new_bank_account
    assert updated.description == "New desc"
    assert updated.tags == {"new", "vip"}
    assert updated.role == CompanyType.CLIENT
    assert updated.updated_by_user_id == TEST_USER_ID
    assert updated.updated_at is not None


def test_update_company_keeps_tax_number_when_none(
    service,
    company_repo,
    existing_company,
    valid_address,
):
    cmd = UpdateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=existing_company.id,
        actor_user_id=TEST_USER_ID,

        name="Updated",
        role=CompanyType.OWN,
        address=valid_address,
        contact=None,
        description=None,
        tax_number=None,  # 🔥 kluczowy przypadek
        bank_account=None,
        tags=None,
    )

    service.execute(cmd)

    updated = company_repo.get(existing_company.id, TEST_ORG_ID)

    assert updated.tax_number == "1234567890"
    assert updated.name == "Updated"


def test_update_company_can_change_role_and_tags(
    service,
    company_repo,
    existing_company,
    valid_address,
):
    cmd = UpdateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=existing_company.id,
        actor_user_id=TEST_USER_ID,

        name="Updated",
        role=CompanyType.CLIENT,
        address=valid_address,
        contact=None,
        description=None,
        tax_number=None,
        bank_account=None,
        tags={"contractor"},
    )

    service.execute(cmd)

    updated = company_repo.get(existing_company.id, TEST_ORG_ID)

    assert updated.role == CompanyType.CLIENT
    assert updated.tags == {"contractor"}


def test_update_company_duplicate_tax_number_raises(
    service,
    company_repo,
    valid_address,
):
    company_a = Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="A",
        tax_number="1234567890",
        description=None,
        address=valid_address,
        contact=None,
        bank_account=None,

        role=CompanyType.CLIENT,
        tags=set(),
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

    company_b = Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="B",
        tax_number="9876543210",
        description=None,
        address=valid_address,
        contact=None,
        bank_account=None,

        role=CompanyType.CLIENT,
        tags=set(),
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

    company_repo.add(company_a)
    company_repo.add(company_b)

    cmd = UpdateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=company_b.id,
        actor_user_id=TEST_USER_ID,

        name="B updated",
        role=CompanyType.CLIENT,
        address=valid_address,
        contact=None,
        description=None,
        tax_number="1234567890",  # ❌ duplikat
        bank_account=None,
        tags=None,
    )

    with pytest.raises(ValueError, match="Company with this tax number already exists"):
        service.execute(cmd)


def test_update_company_normalizes_tax_number(
    service,
    company_repo,
    valid_address,
):
    company = Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="Test",
        tax_number="1234567890",
        description=None,
        address=valid_address,
        contact=None,
        bank_account=None,

        role=CompanyType.CLIENT,
        tags=set(),
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

    company_repo.add(company)

    cmd = UpdateCompanyCommand(
        organization_id=TEST_ORG_ID,
        company_id=company.id,
        actor_user_id=TEST_USER_ID,

        name="Test Updated",
        role=CompanyType.CLIENT,
        address=valid_address,
        contact=None,
        description=None,
        tax_number="PL 123-456-78-90",  # 👈 brudny NIP
        bank_account=None,
        tags=None,
    )

    service.execute(cmd)

    updated = company_repo.get(company.id, TEST_ORG_ID)
    assert updated.tax_number == "1234567890"
