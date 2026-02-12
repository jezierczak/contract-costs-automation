import pytest
from contract_costs.services.companies.normalize.normalize_service import (
    CompanyNormalizeService,
)
from tests.builders.company_builder import CompanyBuilder
from contract_costs.model.company import Contact


# ============================================================
# TAX NUMBER
# ============================================================

def test_normalize_tax_number_regular():
    service = CompanyNormalizeService()

    company = (
        CompanyBuilder()
        .with_tax_number("PL 123-456-32-18")
        .build()
    )

    normalized = service.normalize(company)

    assert normalized.tax_number == "1234563218"


def test_normalize_tax_number_tmp_placeholder():
    service = CompanyNormalizeService()

    company = (
        CompanyBuilder()
        .with_tax_number("TMP-ABC123")
        .build()
    )

    normalized = service.normalize(company)

    assert normalized.tax_number == "TMP-ABC123"


def test_invalid_tax_number_raises():
    service = CompanyNormalizeService()

    company = (
        CompanyBuilder()
        .with_tax_number("INVALID")
        .build()
    )

    with pytest.raises(ValueError):
        service.normalize(company)


# ============================================================
# PHONE
# ============================================================

def test_normalize_phone_extracts_digits():
    service = CompanyNormalizeService()

    company = (
        CompanyBuilder()
        .with_email(None)
        .with_phone("+48 600-700-800")
        .build()
    )

    normalized = service.normalize(company)

    assert normalized.contact.phone_number == "48600700800"


def test_normalize_phone_returns_none_if_too_short():
    service = CompanyNormalizeService()

    company = (
        CompanyBuilder()
        .with_email(None)
        .with_phone("1234")
        .build()
    )

    normalized = service.normalize(company)

    assert normalized.contact is None


# ============================================================
# EMAIL
# ============================================================

def test_normalize_email_lowercase():
    service = CompanyNormalizeService()

    company = (
        CompanyBuilder()
        .with_email("TEST@EXAMPLE.COM")
        .with_phone(None)
        .build()
    )

    normalized = service.normalize(company)

    assert normalized.contact.email == "test@example.com"


# ============================================================
# BANK ACCOUNT
# ============================================================

def test_normalize_bank_account_removes_spaces_and_prefix():
    service = CompanyNormalizeService()

    company = (
        CompanyBuilder()
        .with_bank_account("PL 12 3456 7890 1234 5678 9012 3456")
        .build()
    )

    normalized = service.normalize(company)

    assert normalized.bank_account.account_number == "12345678901234567890123456"


def test_invalid_bank_account_becomes_none():
    service = CompanyNormalizeService()

    company = (
        CompanyBuilder()
        .with_bank_account("INVALID")
        .build()
    )

    normalized = service.normalize(company)

    assert normalized.bank_account is None


# ============================================================
# CONTACT + BANK BOTH NONE
# ============================================================

def test_normalize_keeps_none_fields():
    service = CompanyNormalizeService()

    company = CompanyBuilder().build()

    normalized = service.normalize(company)

    assert normalized.contact is None or normalized.contact.phone_number is None
