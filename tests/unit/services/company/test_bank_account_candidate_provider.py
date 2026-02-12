from contract_costs.common.ids import new_uuid
from contract_costs.services.companies.providers.bank import BankAccountCandidateProvider

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from tests.builders.company_builder import CompanyBuilder


def build_input(bank_account=None):
    return CompanyInput(
        name=None,
        tax_number=None,
        state=None,
        street=None,
        zip_code=None,
        city=None,
        phone_number=None,
        email=None,
        country=None,
        bank_account=bank_account,
        role="supplier",
    )


def test_returns_empty_when_no_bank_account(company_repo):
    provider = BankAccountCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=new_uuid(),
        input_=build_input(),
    )

    assert result == []


def test_returns_empty_when_invalid_bank_account(company_repo):
    provider = BankAccountCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=new_uuid(),
        input_=build_input(bank_account="INVALID"),
    )

    assert result == []


def test_returns_matching_company(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_bank_account("12345678901234567890123456")
        .build()
    )

    company_repo.add(company)

    provider = BankAccountCandidateProvider(company_repo)

    result = provider.find_candidates(
        organization_id=org_id,
        input_=build_input(bank_account="1234 5678 9012 3456 7890 1234 56"),
    )

    assert len(result) == 1
    assert result[0].id == company.id
