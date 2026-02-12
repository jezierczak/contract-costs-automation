import pytest


from contract_costs.common.ids import new_uuid
from contract_costs.model.company import CompanyType
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator, EvaluateMode
from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider

from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from tests.builders.company_builder import CompanyBuilder


# ============================================================
# FAKE CANDIDATE PROVIDER
# ============================================================

class FakeCandidateProvider(CompanyCandidateProvider):
    def __init__(self):
        self._candidates = []

    def set_candidates(self, items):
        self._candidates = items

    def find_candidates(self, *, organization_id, input_):
        return self._candidates


# ============================================================
# HELPERS
# ============================================================

def build_input(
    *,
    name="ACME",
    tax="1234567890",
    email=None,
    phone=None,
    role=CompanyType.SUPPLIER,
):
    return CompanyInput(
        name=name,
        tax_number=tax,
        state=None,
        street=None,
        zip_code=None,
        city=None,
        phone_number=phone,
        email=email,
        country=None,
        bank_account=None,
        role=role.value,
    )


# ============================================================
# TESTS
# ============================================================


def test_creates_company_when_no_candidates(company_repo):
    provider = FakeCandidateProvider()
    provider.set_candidates([])

    orchestrator = CompanyEvaluateOrchestrator(
        company_repo,
        provider,
        llm_company_resolver=None,
    )

    org_id = new_uuid()

    result = orchestrator.evaluate(
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=build_input(),
    )

    assert result.name == "ACME"
    assert result.tax_number == "1234567890"
    assert result.is_active is True


def test_no_create_mode_raises(company_repo):
    provider = FakeCandidateProvider()
    provider.set_candidates([])

    orchestrator = CompanyEvaluateOrchestrator(
        company_repo,
        provider,
        llm_company_resolver=None,
    )

    with pytest.raises(RuntimeError):
        orchestrator.evaluate(
            organization_id=new_uuid(),
            actor_user_id=new_uuid(),
            input_=build_input(),
            mode=EvaluateMode.NO_CREATE,
        )


def test_prefers_active_own_candidate(company_repo):
    org_id = new_uuid()

    own = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .build()
    )

    supplier = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .build()
    )

    company_repo.add(own)
    company_repo.add(supplier)

    provider = FakeCandidateProvider()
    provider.set_candidates([supplier, own])

    orchestrator = CompanyEvaluateOrchestrator(
        company_repo,
        provider,
        llm_company_resolver=None,
    )

    result = orchestrator.evaluate(
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=build_input(),
    )

    assert result.id == own.id


def test_soft_update_updates_missing_email(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .build()
    )

    company_repo.add(company)

    provider = FakeCandidateProvider()
    provider.set_candidates([company])

    orchestrator = CompanyEvaluateOrchestrator(
        company_repo,
        provider,
        llm_company_resolver=None,
    )

    input_ = build_input(email="new@email.com")

    updated = orchestrator.evaluate(
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=input_,
    )

    assert updated.contact.email == "new@email.com"


def test_authoritative_mode_forces_update(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("OLD NAME")
        .build()
    )

    company_repo.add(company)

    provider = FakeCandidateProvider()
    provider.set_candidates([company])

    orchestrator = CompanyEvaluateOrchestrator(
        company_repo,
        provider,
        llm_company_resolver=None,
    )

    input_ = build_input(name="NEW NAME")

    updated = orchestrator.evaluate(
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=input_,
        mode=EvaluateMode.AUTHORITATIVE,
    )

    assert updated.name == "NEW NAME"
    assert updated.updated_at is not None


def test_no_change_does_not_update_timestamp(company_repo):
    org_id = new_uuid()

    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("ACME")
        .build()
    )

    company_repo.add(company)

    provider = FakeCandidateProvider()
    provider.set_candidates([company])

    orchestrator = CompanyEvaluateOrchestrator(
        company_repo,
        provider,
        llm_company_resolver=None,
    )

    input_ = build_input(name="ACME")

    updated = orchestrator.evaluate(
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=input_,
    )

    assert updated.updated_at is None
