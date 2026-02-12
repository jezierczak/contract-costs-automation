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

def test_returns_empty_when_no_tax_number(company_repo):
    provider = ExactNipCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=new_uuid(),
        input_=build_input(),
    )

    assert result == []


def test_returns_company_when_exact_nip_matches(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1234567890")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(tax_number="1234567890"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


# ------------------------------------------------------------
# NORMALIZATION
# ------------------------------------------------------------

def test_normalizes_tax_number_before_matching(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("1234567890")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(tax_number="PL 123-456-78-90"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


# ------------------------------------------------------------
# PLACEHOLDER FALLBACK
# ------------------------------------------------------------

def test_matches_tmp_placeholder(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("TMP-ABC123")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(tax_number="TMP-ABC123"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


def test_matches_ai_placeholder(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_tax_number("AI-XYZ999")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(tax_number="AI-XYZ999"),
    )

    assert len(result) == 1


# ------------------------------------------------------------
# SCOPING
# ------------------------------------------------------------

def test_is_scoped_to_organization(company_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org1)
        .with_tax_number("1234567890")
        .build()
    )

    company_repo.add(company)

    provider = ExactNipCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org2,
        input_=build_input(tax_number="1234567890"),
    )

    assert result == []
