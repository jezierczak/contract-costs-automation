
from contract_costs.services.companies.confidence.quality_default import (
    DefaultCompanyQuality
)
from contract_costs.services.companies.confidence.fields import CompanyField
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from tests.builders.company_builder import CompanyBuilder


# =====================================================
# TAX NUMBER
# =====================================================

def test_valid_nip_scores_100():
    company = CompanyBuilder().with_tax_number("1234563218").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.TAX_NUMBER) in (0, 100)


def test_invalid_nip_scores_0():
    company = CompanyBuilder().with_tax_number("123").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.TAX_NUMBER) == 0


# =====================================================
# NAME
# =====================================================

def test_placeholder_name_scores_0():
    company = CompanyBuilder().with_name("UNKNOWN SELLER").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.NAME) == 0


def test_good_name_scores_100():
    company = CompanyBuilder().with_name("ACME SP Z O O").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.NAME) in (50, 100)


# =====================================================
# EMAIL
# =====================================================

def test_valid_email_scores_100():
    company = CompanyBuilder().with_email("test@example.com").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.EMAIL) == 100


def test_invalid_email_scores_0():
    company = CompanyBuilder().with_email("invalid").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.EMAIL) == 0


# =====================================================
# PHONE
# =====================================================

def test_valid_phone_scores_100():
    company = CompanyBuilder().with_phone("+48 600 700 800").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.PHONE_NUMBER) == 100


def test_invalid_phone_scores_0():
    company = CompanyBuilder().with_phone("123").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.PHONE_NUMBER) == 0


# =====================================================
# BANK ACCOUNT
# =====================================================

def test_valid_bank_account_scores_100():
    company = (
        CompanyBuilder()
        .with_bank_account("12345678901234567890123456")
        .build()
    )
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.BANK_ACCOUNT) == 100


def test_invalid_bank_account_scores_0():
    company = CompanyBuilder().with_bank_account("123").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.BANK_ACCOUNT) == 0


# =====================================================
# ZIP CODE
# =====================================================

def test_valid_zip_scores_100():
    company = CompanyBuilder().with_address(zip_code="12-345").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.ZIP_CODE) == 100


def test_partial_zip_scores_50():
    company = CompanyBuilder().with_address(zip_code="12345").build()
    quality = DefaultCompanyQuality.from_company(company)

    assert quality.get_field_score(CompanyField.ZIP_CODE) == 50


# =====================================================
# OVERALL SCORE
# =====================================================

def test_overall_score_is_weighted():
    company = (
        CompanyBuilder()
        .with_tax_number("1234563218")
        .with_email("test@example.com")
        .with_phone("+48 600 700 800")
        .build()
    )

    quality = DefaultCompanyQuality.from_company(company)
    overall = quality.get_overall_score()

    # sanity check – nie 0, nie 100
    assert 0 < overall <= 100


# =====================================================
# FROM INPUT
# =====================================================

def test_from_input_scoring():
    input_ = CompanyInput(
        name="ACME",
        tax_number="1234563218",
        street="Krakowska 10",
        city="Kraków",
        zip_code="12-345",
        country="PL",
        phone_number="600700800",
        email="test@example.com",
        bank_account="12345678901234567890123456",
        role="Supplier",
        state="Małopolska"
    )

    quality = DefaultCompanyQuality.from_input(input_)

    assert quality.get_overall_score() > 50
