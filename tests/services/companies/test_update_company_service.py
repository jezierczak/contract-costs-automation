import pytest
from uuid import uuid4

from contract_costs.model.company import (
    Company,
    CompanyType,
    Address,
    Contact,
    BankAccount,
)
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.update_company_service import UpdateCompanyService


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
        name="Old name",
        tax_number="1234567890",
        address=None,
        contact=None,
        bank_account=None,
        role=CompanyType.OWN,
        description="Old desc",
        tags={"old"},
        is_active=True,
    )
    company_repo.add(company)
    return company


@pytest.fixture
def new_address():
    return Address(
        street="Main",
        city="Warsaw",
        zip_code="00-001",
        country="PL",
    )
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
        number="12345678901234567890123456",
        country_code="PL",
    )


# --------------------------------------------------
# TESTS
# --------------------------------------------------
def test_update_company_not_existing_raises(service, valid_address):
    with pytest.raises(ValueError, match="Company does not exist"):
        service.execute(
            company_id=uuid4(),
            name="X",
            address=valid_address,
            role=CompanyType.CLIENT,
        )

def test_update_company_updates_all_fields(
    service,
    company_repo,
    existing_company,
    new_address,
    new_contact,
    new_bank_account,
):
    service.execute(
        company_id=existing_company.id,
        name="New name",
        address=new_address,
        contact=new_contact,
        role=CompanyType.CLIENT,
        tax_number="9999999999",
        description="New desc",
        bank_account=new_bank_account,
        tags={"new", "vip"},
    )

    updated = company_repo.get(existing_company.id)

    assert updated.name == "New name"
    assert updated.tax_number == "9999999999"
    assert updated.address == new_address
    assert updated.contact == new_contact
    assert updated.bank_account == new_bank_account
    assert updated.description == "New desc"
    assert updated.tags == {"new", "vip"}
    assert updated.role == CompanyType.CLIENT


def test_update_company_keeps_tax_number_when_none(
    service,
    company_repo,
    existing_company,
    new_address,
):
    service.execute(
        company_id=existing_company.id,
        name="Updated",
        address=new_address,
        role=CompanyType.OWN,
        tax_number=None,  # 🔥 kluczowy przypadek
    )

    updated = company_repo.get(existing_company.id)

    assert updated.tax_number == "1234567890"  # NIE zmieniony
    assert updated.name == "Updated"


def test_update_company_can_change_role_and_tags(
    service,
    company_repo,
    existing_company,
    new_address,
):
    service.execute(
        company_id=existing_company.id,
        name="Updated",
        address=new_address,
        role=CompanyType.CLIENT,
        tags={"contractor"},
    )

    updated = company_repo.get(existing_company.id)

    assert updated.role == CompanyType.CLIENT
    assert updated.tags == {"contractor"}


def test_update_company_duplicate_tax_number_raises(
    service,
    company_repo,
    valid_address,
):
    # firma A
    company_a = Company(
        id=uuid4(),
        name="A",
        tax_number="1234567890",
        address=valid_address,
        contact=None,
        role=CompanyType.CLIENT,
        description=None,
        bank_account=None,
        tags=set(),
        is_active=True,
    )

    # firma B
    company_b = Company(
        id=uuid4(),
        name="B",
        tax_number="9876543210",
        address=valid_address,
        contact=None,
        role=CompanyType.CLIENT,
        description=None,
        bank_account=None,
        tags=set(),
        is_active=True,
    )

    company_repo.add(company_a)
    company_repo.add(company_b)

    with pytest.raises(ValueError, match="Company with this tax number already exists"):
        service.execute(
            company_id=company_b.id,
            name="B updated",
            address=valid_address,
            role=CompanyType.CLIENT,
            tax_number="1234567890",  # ❌ NIP firmy A
        )

def test_update_company_normalizes_tax_number(
    service,
    company_repo,
    valid_address,
):
    company = Company(
        id=uuid4(),
        name="Test",
        tax_number="1234567890",
        address=valid_address,
        contact=None,
        role=CompanyType.CLIENT,
        description=None,
        bank_account=None,
        tags=set(),
        is_active=True,
    )

    company_repo.add(company)

    service.execute(
        company_id=company.id,
        name="Test Updated",
        address=valid_address,
        role=CompanyType.CLIENT,
        tax_number="PL 123-456-78-90",  # 👈 brudny NIP
    )

    updated = company_repo.get(company.id)
    assert updated.tax_number == "1234567890"
