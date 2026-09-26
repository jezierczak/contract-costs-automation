from contract_costs.common.ids import new_uuid
from contract_costs.services.companies.providers.excact_nip import ExactNipCandidateProvider

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from tests.builders.company_builder import CompanyBuilder


def build_input(tax_number=None):
    return CompanyInput(
        name=None,
        tax_number=tax_number,
        state=None,
        street=None,
        zip_code=None,
        city=None,
        phone_number=None,
        email=None,
        country=None,
        bank_account=None,
        role="supplier",
    )


# ------------------------------------------------------------
# BASIC
# ------------------------------------------------------------

def test_returns_empty_when_no_tax_number(uow):
    provider = ExactNipCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=new_uuid(),
        input_=build_input(),
    )

    assert result == []


def test_returns_company_when_exact_nip_matches(company_repo, uow):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1234567890")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input(tax_number="1234567890"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


# ------------------------------------------------------------
# NORMALIZATION
# ------------------------------------------------------------

def test_normalizes_tax_number_before_matching(company_repo, uow):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1234567890")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input(tax_number="PL 123-456-78-90"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


# ------------------------------------------------------------
# PLACEHOLDER FALLBACK
# ------------------------------------------------------------

def test_matches_tmp_placeholder(company_repo, uow):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("TMP-ABC123")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input(tax_number="TMP-ABC123"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


def test_matches_ai_placeholder(company_repo, uow):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("AI-XYZ999")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input(tax_number="AI-XYZ999"),
    )

    assert len(result) == 1


# ------------------------------------------------------------
# SCOPING
# ------------------------------------------------------------

def test_is_scoped_to_organization(company_repo, uow):
    org1 = new_uuid()
    org2 = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org1)
        .with_tax_number("1234567890")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org2,
        input_=build_input(tax_number="1234567890"),
    )

    assert result == []


# ------------------------------------------------------------
# PREFIKS KRAJU (numer zapisany z literami lub bez)
# ------------------------------------------------------------

def _add(company_repo, org_id, tax_number):
    company = CompanyBuilder().with_organization_id(org_id).with_tax_number(tax_number).build()
    company_repo.add(company)
    return company


def _find(uow, org_id, tax_number):
    return ExactNipCandidateProvider().find_candidates(
        uow=uow, organization_id=org_id, input_=build_input(tax_number=tax_number),
    )


def test_prefixed_input_matches_company_saved_without_letters(company_repo, uow):
    org_id = new_uuid()
    company = _add(company_repo, org_id, "123456789")

    result = _find(uow, org_id, "DE123456789")

    assert [c.id for c in result] == [company.id]


def test_digits_input_matches_company_saved_with_prefix(company_repo, uow):
    org_id = new_uuid()
    company = _add(company_repo, org_id, "DE123456789")

    result = _find(uow, org_id, "123456789")

    assert [c.id for c in result] == [company.id]


def test_letters_inside_number_are_ignored_too(company_repo, uow):
    org_id = new_uuid()
    company = _add(company_repo, org_id, "12345678901")

    result = _find(uow, org_id, "NL123456789B01")

    assert [c.id for c in result] == [company.id]


def test_exact_match_wins_over_digits_match(company_repo, uow):
    org_id = new_uuid()
    _add(company_repo, org_id, "DE123456789")
    exact = _add(company_repo, org_id, "123456789")

    result = _find(uow, org_id, "123456789")

    assert [c.id for c in result] == [exact.id]


def test_ambiguous_digits_match_returns_nothing(company_repo, uow):
    org_id = new_uuid()
    _add(company_repo, org_id, "DE123456789")
    _add(company_repo, org_id, "AT123456789")

    assert _find(uow, org_id, "123456789") == []


def test_digits_match_ignores_placeholders(company_repo, uow):
    org_id = new_uuid()
    _add(company_repo, org_id, "OTH-000001")

    assert _find(uow, org_id, "DE000001") == []


def test_digits_match_is_scoped_to_organization(company_repo, uow):
    _add(company_repo, new_uuid(), "123456789")

    assert _find(uow, new_uuid(), "DE123456789") == []
