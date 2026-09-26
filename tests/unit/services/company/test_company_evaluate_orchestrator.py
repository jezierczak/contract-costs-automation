import pytest


from contract_costs.common.ids import new_uuid
from contract_costs.model.company import CompanyType, CompanyVerificationStatus
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

    def find_candidates(self, *, uow, organization_id, input_):
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


def build_orchestrator(suggestions=None) -> CompanyEvaluateOrchestrator:
    provider = FakeCandidateProvider()
    provider.set_candidates(suggestions or [])
    return CompanyEvaluateOrchestrator(provider, llm_company_resolver=None)


# ============================================================
# TESTS
# ============================================================


def test_creates_company_when_no_candidates(uow):
    result = build_orchestrator().evaluate(
        uow=uow,
        organization_id=new_uuid(),
        actor_user_id=new_uuid(),
        input_=build_input(),
    )

    assert result.name == "ACME"
    assert result.tax_number == "1234567890"
    assert result.is_active is True


def test_no_create_mode_raises(uow):
    with pytest.raises(RuntimeError):
        build_orchestrator().evaluate(
            uow=uow,
            organization_id=new_uuid(),
            actor_user_id=new_uuid(),
            input_=build_input(),
            mode=EvaluateMode.NO_CREATE,
        )


def test_matches_only_by_exact_tax_number(company_repo, uow):
    org_id = new_uuid()
    by_nip = CompanyBuilder().with_organization_id(org_id).with_tax_number("1234567890").build()
    own = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_tax_number("5555555555")
        .build()
    )
    company_repo.add(by_nip)
    company_repo.add(own)

    # fuzzy podpowiedź (nawet OWN) nie wygrywa z dokładnym NIP-em
    result = build_orchestrator(suggestions=[own]).evaluate(
        uow=uow,
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=build_input(),
    )

    assert result.id == by_nip.id


def test_fuzzy_candidates_do_not_block_creation(company_repo, uow):
    org_id = new_uuid()
    similar = CompanyBuilder().with_organization_id(org_id).with_tax_number("5555555555").build()
    company_repo.add(similar)

    result = build_orchestrator(suggestions=[similar]).evaluate(
        uow=uow,
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=build_input(),
    )

    assert result.id != similar.id
    assert result.tax_number == "1234567890"


def test_suggest_returns_fuzzy_candidates(uow):
    similar = CompanyBuilder().build()

    assert build_orchestrator(suggestions=[similar]).suggest(
        uow=uow,
        organization_id=new_uuid(),
        input_=build_input(),
    ) == [similar]


def test_normal_mode_fills_missing_email(company_repo, uow):
    org_id = new_uuid()
    company = CompanyBuilder().with_organization_id(org_id).build()
    company_repo.add(company)

    updated = build_orchestrator().evaluate(
        uow=uow,
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=build_input(email="new@email.com"),
    )

    assert updated.contact.email == "new@email.com"
    assert company_repo.get(company.id, org_id).contact.email == "new@email.com"


def test_normal_mode_does_not_overwrite_existing_data(company_repo, uow):
    org_id = new_uuid()
    company = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("OLD NAME")
        .with_email("old@email.com")
        .build()
    )
    company_repo.add(company)

    updated = build_orchestrator().evaluate(
        uow=uow,
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=build_input(name="NEW NAME", email="new@email.com"),
    )

    assert updated.name == "OLD NAME"
    assert updated.contact.email == "old@email.com"
    assert updated.updated_at is None


def test_authoritative_mode_overwrites_data(company_repo, uow):
    org_id = new_uuid()
    company = CompanyBuilder().with_organization_id(org_id).with_name("OLD NAME").build()
    company_repo.add(company)

    updated = build_orchestrator().evaluate(
        uow=uow,
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=build_input(name="NEW NAME"),
        mode=EvaluateMode.AUTHORITATIVE,
    )

    assert updated.name == "NEW NAME"
    assert updated.tax_number == "1234567890"
    assert updated.updated_at is not None


def test_no_change_does_not_update_timestamp(company_repo, uow):
    org_id = new_uuid()
    company = CompanyBuilder().with_organization_id(org_id).with_name("ACME").build()
    company_repo.add(company)

    updated = build_orchestrator().evaluate(
        uow=uow,
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=build_input(name="ACME"),
        mode=EvaluateMode.AUTHORITATIVE,
    )

    assert updated.updated_at is None


@pytest.mark.parametrize(
    ("name", "tax", "expected"),
    [
        ("ACME", "5261009959", CompanyVerificationStatus.VERIFIED),       # poprawna suma kontrolna
        ("ACME", "IE3463004VH", CompanyVerificationStatus.VERIFIED),      # VAT UE z prefiksem
        ("ACME", "1234567890", CompanyVerificationStatus.TO_VERIFY),      # zła suma kontrolna
        ("ACME", None, CompanyVerificationStatus.TO_VERIFY),              # brak NIP → TMP-
        (None, "5261009959", CompanyVerificationStatus.TO_VERIFY),        # brak nazwy
    ],
)
def test_created_company_verification_status(uow, name, tax, expected):
    result = build_orchestrator().evaluate(
        uow=uow,
        organization_id=new_uuid(),
        actor_user_id=new_uuid(),
        input_=build_input(name=name, tax=tax),
    )

    assert result.verification_status == expected
