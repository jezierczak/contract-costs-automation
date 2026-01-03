import pytest
from uuid import uuid4

from contract_costs.model.company import Company, Address, Contact, BankAccount, CompanyType
from contract_costs.services.companies.normalize.normalize_service import CompanyNormalizeService


def make_company(
    *,
    tax_number=None,
    phone=None,
    email=None,
    bank_account=None,
):
    return Company(
        id=uuid4(),
        name="Test Company",
        description=None,
        tax_number=tax_number,
        address=Address("", "", "", ""),
        contact=Contact(phone, email) if phone or email else None,
        bank_account=BankAccount(bank_account) if bank_account else None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
    )

def test_normalize_tax_number():
    service = CompanyNormalizeService()

    company = make_company(tax_number="532-010-13-03")
    normalized = service.normalize(company)

    assert normalized.tax_number == "5320101303"


def test_placeholder_tax_number_not_modified():
    service = CompanyNormalizeService()

    company = make_company(tax_number="TMP-abc123")
    normalized = service.normalize(company)

    assert normalized.tax_number == "TMP-abc123"

def test_normalize_phone_multiple_numbers():
    service = CompanyNormalizeService()

    company = make_company(phone="(032) 615 54 55, 615 60 27")
    normalized = service.normalize(company)

    assert normalized.contact.phone_number == "0326155455"


def test_normalize_phone_with_pl_prefix():
    service = CompanyNormalizeService()

    company = make_company(phone="+48 501 234 567")
    normalized = service.normalize(company)

    assert normalized.contact.phone_number == "48501234567"

def test_invalid_phone_removed():
    service = CompanyNormalizeService()

    company = make_company(phone="abc def ghi")
    normalized = service.normalize(company)

    assert normalized.contact is None

def test_normalize_email():
    service = CompanyNormalizeService()

    company = make_company(email="  TEST@EXAMPLE.COM ")
    normalized = service.normalize(company)

    assert normalized.contact.email == "test@example.com"

def test_no_contact_if_email_and_phone_empty():
    service = CompanyNormalizeService()

    company = make_company()
    normalized = service.normalize(company)

    assert normalized.contact is None

def test_normalize_bank_account():
    service = CompanyNormalizeService()

    company = make_company(bank_account="PL 10-1050 1302 1000 0008 0782 0911")
    normalized = service.normalize(company)

    assert normalized.bank_account.number == "10105013021000000807820911"

def test_no_bank_account_if_invalid():
    service = CompanyNormalizeService()

    company = make_company(bank_account="--- ---")
    normalized = service.normalize(company)

    assert normalized.bank_account is None

def test_does_not_create_empty_contact_or_bank_account():
    service = CompanyNormalizeService()

    company = make_company(
        phone="invalid",
        email="",
        bank_account="",
    )

    normalized = service.normalize(company)

    assert normalized.contact is None
    assert normalized.bank_account is None


def test_company_normalize_never_sets_none_tax_number():
    company = make_company(tax_number="PL 123-456-78-90")
    normalized = CompanyNormalizeService().normalize(company)
    assert normalized.tax_number is not None
