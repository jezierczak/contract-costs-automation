import pytest

from tests.builders.company_builder import CompanyBuilder
from contract_costs.services.companies.normalize.normalize_service import (
    CompanyNormalizeService,
)


def test_company_normalize_service_normalizes_contact_bank_and_tax_number() -> None:
    company = (
        CompanyBuilder()
        .with_tax_number("PL 676-268-01-95")
        .with_phone("+48 123-456-789")
        .with_email("  USER@EXAMPLE.COM ")
        .with_bank_account("PL 65 1030 1188 0000 0000 5983 0200", "PL")
        .build()
    )

    normalized = CompanyNormalizeService().normalize(company)

    assert normalized.tax_number == "6762680195"
    assert normalized.contact is not None
    assert normalized.contact.phone_number == "48123456789"
    assert normalized.contact.email == "user@example.com"
    assert normalized.bank_account is not None
    assert normalized.bank_account.account_number == "65103011880000000059830200"


def test_company_normalize_service_keeps_tmp_tax_number_and_invalid_bank_as_none() -> None:
    company = (
        CompanyBuilder()
        .with_tax_number("TMP-abc")
        .with_bank_account("NOT_A_BANK", "PL")
        .build()
    )

    normalized = CompanyNormalizeService().normalize(company)

    assert normalized.tax_number == "TMP-abc"
    assert normalized.bank_account is None


def test_company_normalize_service_raises_for_invalid_tax_number() -> None:
    company = CompanyBuilder().with_tax_number("abc").build()

    with pytest.raises(ValueError, match="Invalid tax_number"):
        CompanyNormalizeService().normalize(company)


def test_company_normalize_helpers() -> None:
    svc = CompanyNormalizeService()

    assert svc.normalize_tax_number(None) is None
    assert svc.normalize_tax_number("TMP-1") == "TMP-1"
    assert svc.normalize_bank_account("PL 65 1030 1188 0000 0000 5983 0200") == "65103011880000000059830200"
    assert svc.normalize_bank_account("abc") is None
    assert svc.normalize_phone("(123) 456-789") == "123456789"
    assert svc.normalize_email(" A@B.COM ") == "a@b.com"

