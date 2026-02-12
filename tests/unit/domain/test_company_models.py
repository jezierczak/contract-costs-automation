import pytest

from contract_costs.model.company import Address, BankAccount, CompanyType, Company
from tests.builders.company_builder import CompanyBuilder


def test_address_accepts_valid_polish_zip():
    address = Address(
        street="Testowa 1",
        city="Kraków",
        zip_code="12-345",
        country="PL",
    )

    assert address.zip_code == "12-345"


def test_address_invalid_polish_zip_does_not_raise():
    address = Address(
        street="Test",
        city="City",
        zip_code="12345",
        country="PL",
    )

    assert address.zip_code == "12345"

def test_address_without_country_skips_validation():
    address = Address(
        street="Test",
        city="City",
        zip_code="BADZIP",
        country=None,
    )

    assert address.zip_code == "BADZIP"


def test_bank_account_removes_spaces():
    account = BankAccount(
        account_number="12 3456 7890 1234 5678 9012 34",
        country_code="pl",
    )

    assert account.account_number == "123456789012345678901234"
    assert account.country_code == "PL"


def test_bank_account_invalid_country_code():
    with pytest.raises(ValueError):
        BankAccount(
            account_number="123",
            country_code="POL",
        )

def test_iban_generation():
    account = BankAccount(
        account_number="12345678901234567890123456",
        country_code="PL",
    )

    assert account.iban == "PL12345678901234567890123456"

def test_polish_account_wrong_length_does_not_raise():
    account = BankAccount(
        account_number="123",
        country_code="PL",
    )

    assert account.account_number == "123"



def test_company_creation():
    company = CompanyBuilder().build()

    assert company.name == "Test Company"
    assert company.is_active is True
    assert company.tags == set()

def test_company_is_mutable():
    company = CompanyBuilder().build()

    company.name = "New Name"

    assert company.name == "New Name"

def test_company_has_base_entity_fields():
    company = CompanyBuilder().build()

    assert company.organization_id is not None
    assert company.created_at is not None

def test_company_tags_are_independent():
    c1 = CompanyBuilder().build()
    c2 = CompanyBuilder().build()

    c1.tags.add("VIP")

    assert "VIP" in c1.tags
    assert "VIP" not in c2.tags


def test_company_cannot_add_new_attributes():
    company = CompanyBuilder().build()

    with pytest.raises(AttributeError):
        company.some_random_field = "boom"

def test_bank_account_is_immutable():
    account = BankAccount(
        account_number="12345678901234567890123456",
        country_code="PL",
    )

    with pytest.raises(Exception):
        account.account_number = "999"
