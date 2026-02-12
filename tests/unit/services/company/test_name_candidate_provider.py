from contract_costs.common.ids import new_uuid
from contract_costs.services.companies.providers.name import NameCandidateProvider
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from tests.builders.company_builder import CompanyBuilder


def build_input(name=None):
    return CompanyInput(
        name=name,
        tax_number=None,
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

def test_returns_empty_when_name_missing(company_repo):
    provider = NameCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=new_uuid(),
        input_=build_input(),
    )

    assert result == []


def test_returns_empty_when_name_too_short(company_repo):
    provider = NameCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=new_uuid(),
        input_=build_input(name="A"),
    )

    assert result == []


# ------------------------------------------------------------
# HARD MATCH
# ------------------------------------------------------------

def test_returns_exact_normalized_match(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("ACME Sp. z o.o.")
        .build()
    )

    company_repo.add(company)

    provider = NameCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(name="acme sp z o o"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


# ------------------------------------------------------------
# SOFT MATCH (substring)
# ------------------------------------------------------------

def test_returns_soft_match_when_substring(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("Mega Construction Group")
        .build()
    )

    company_repo.add(company)

    provider = NameCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(name="Mega Construction"),
    )

    assert len(result) == 1


def test_returns_multiple_when_multiple_match(company_repo):
    org_id = new_uuid()

    c1 = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("Alpha Tech")
        .build()
    )

    c2 = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("Alpha Systems")
        .build()
    )

    company_repo.add(c1)
    company_repo.add(c2)

    provider = NameCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(name="Alpha"),
    )

    assert len(result) == 2


# ------------------------------------------------------------
# SCOPING
# ------------------------------------------------------------

def test_is_scoped_to_organization(company_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org1)
        .with_name("Scoped Company")
        .build()
    )

    company_repo.add(company)

    provider = NameCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org2,
        input_=build_input(name="Scoped"),
    )

    assert result == []
