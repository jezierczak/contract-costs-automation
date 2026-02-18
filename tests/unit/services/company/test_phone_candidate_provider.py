from contract_costs.common.ids import new_uuid
from contract_costs.services.companies.providers.phone import PhoneCandidateProvider
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from tests.builders.company_builder import CompanyBuilder


def build_input(phone=None):
    return CompanyInput(
        name=None,
        tax_number=None,
        state=None,
        street=None,
        zip_code=None,
        city=None,
        phone_number=phone,
        email=None,
        country=None,
        bank_account=None,
        role="supplier",
    )


# ------------------------------------------------------------
# BASIC GUARDS
# ------------------------------------------------------------

def test_returns_empty_when_phone_missing(uow):
    provider = PhoneCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=new_uuid(),
        input_=build_input(),
    )

    assert result == []


def test_returns_empty_when_phone_invalid(uow):
    provider = PhoneCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=new_uuid(),
        input_=build_input(phone="123"),
    )

    assert result == []


# ------------------------------------------------------------
# NORMALIZATION
# ------------------------------------------------------------

def test_matches_phone_with_spaces_and_prefix(company_repo, uow):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_phone("123456789")
        .build()
    )

    company_repo.add(company)

    provider = PhoneCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input(phone="+48 123 456 789"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


def test_matches_phone_with_dashes(company_repo, uow):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_phone("987654321")
        .build()
    )

    company_repo.add(company)

    provider = PhoneCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input(phone="987-654-321"),
    )

    assert len(result) == 1


# ------------------------------------------------------------
# MULTIPLE RESULTS
# ------------------------------------------------------------

def test_returns_multiple_when_many_have_same_phone(company_repo, uow):
    org_id = new_uuid()

    c1 = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_phone("555666777")
        .build()
    )

    c2 = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_phone("555666777")
        .build()
    )

    company_repo.add(c1)
    company_repo.add(c2)

    provider = PhoneCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org_id,
        input_=build_input(phone="555666777"),
    )

    assert len(result) == 2


# ------------------------------------------------------------
# ORGANIZATION SCOPING
# ------------------------------------------------------------

def test_scoped_to_organization(company_repo, uow):
    org1 = new_uuid()
    org2 = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org1)
        .with_phone("111222333")
        .build()
    )

    company_repo.add(company)

    provider = PhoneCandidateProvider()

    result = provider.find_candidates(
        uow=uow,
        organization_id=org2,
        input_=build_input(phone="111222333"),
    )

    assert result == []
