from contract_costs.common.ids import new_uuid
from contract_costs.services.companies.providers.street import StreetCandidateProvider

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from tests.builders.company_builder import CompanyBuilder


def build_input(street=None):
    return CompanyInput(
        name=None,
        tax_number=None,
        state=None,
        street=street,
        zip_code=None,
        city=None,
        phone_number=None,
        email=None,
        country=None,
        bank_account=None,
        role="supplier",
    )


# ------------------------------------------------------------
# BASIC GUARDS
# ------------------------------------------------------------

def test_returns_empty_when_no_street(uow):
    provider = StreetCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=new_uuid(),
        input_=build_input(),
    )

    assert result == []


def test_returns_empty_when_no_tokens(uow):
    provider = StreetCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=new_uuid(),
        input_=build_input("12"),
    )

    assert result == []


# ------------------------------------------------------------
# MATCH BY NUMBER + TOKEN
# ------------------------------------------------------------

def test_match_by_same_number_and_token(company_repo, uow):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_street("Krakowska 12")
        .build()
    )

    company_repo.add(company)

    provider = StreetCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input("ul. Krakowska 12"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


# ------------------------------------------------------------
# MATCH BY TOKENS ONLY (NO NUMBER)
# ------------------------------------------------------------

def test_match_by_two_common_tokens(company_repo, uow):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_street("Aleja Jana Pawla")
        .build()
    )

    company_repo.add(company)

    provider = StreetCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input("Jana Pawla"),
    )

    assert len(result) == 1


# ------------------------------------------------------------
# NO MATCH WHEN ONLY ONE TOKEN
# ------------------------------------------------------------

def test_no_match_with_single_common_token(company_repo, uow):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_street("Jana Pawla")
        .build()
    )

    company_repo.add(company)

    provider = StreetCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input("Jana"),
    )

    assert result == []


# ------------------------------------------------------------
# ORGANIZATION SCOPING
# ------------------------------------------------------------

def test_scoped_to_organization(company_repo, uow):
    org1 = new_uuid()
    org2 = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org1)
        .with_street("Krakowska 12")
        .build()
    )

    company_repo.add(company)

    provider = StreetCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org2,
        input_=build_input("Krakowska 12"),
    )

    assert result == []
