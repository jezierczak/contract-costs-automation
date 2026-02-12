from contract_costs.common.ids import new_uuid
from contract_costs.services.companies.providers.email import EmailCandidateProvider

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from tests.builders.company_builder import CompanyBuilder


def build_input(email=None):
    return CompanyInput(
        name=None,
        tax_number=None,
        state=None,
        street=None,
        zip_code=None,
        city=None,
        phone_number=None,
        email=email,
        country=None,
        bank_account=None,
        role="supplier",
    )


def test_returns_empty_when_no_email(company_repo):
    provider = EmailCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=new_uuid(),
        input_=build_input(),
    )

    assert result == []


def test_returns_empty_when_no_match(company_repo):
    org_id = new_uuid()

    provider = EmailCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(email="a@b.com"),
    )

    assert result == []


def test_returns_matching_company(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_email("test@example.com")
        .build()
    )

    company_repo.add(company)

    provider = EmailCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(email="test@example.com"),
    )

    assert len(result) == 1
    assert result[0].id == company.id


def test_is_scoped_to_organization(company_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org1)
        .with_email("test@example.com")
        .build()
    )

    company_repo.add(company)

    provider = EmailCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org2,
        input_=build_input(email="test@example.com"),
    )

    assert result == []
