from unittest.mock import MagicMock
from uuid import uuid4
from datetime import datetime

import pytest

from contract_costs.infrastructure.openai_invoice_client import OpenAIInvoiceClient
from contract_costs.model.company import Company, Address, Contact, CompanyType
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.company_evaluate_orchestrator import (
    CompanyEvaluateOrchestrator,
    EvaluateMode,
)
from contract_costs.services.companies.providers.street import StreetCandidateProvider
from contract_costs.services.companies.providers.bank import BankAccountCandidateProvider
from contract_costs.services.companies.providers.composite import CompositeCompanyCandidateProvider
from contract_costs.services.companies.providers.email import EmailCandidateProvider
from contract_costs.services.companies.providers.excact_nip import ExactNipCandidateProvider
from contract_costs.services.companies.providers.name import NameCandidateProvider
from contract_costs.services.companies.providers.phone import PhoneCandidateProvider
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput


TEST_ORG_ID = uuid4()
TEST_USER_ID = uuid4()
NOW = datetime(2024, 1, 1)


# =====================
# HELPERS
# =====================

def dummy_LLM():
    mock = MagicMock(OpenAIInvoiceClient)
    mock.resolve_company.return_value = None
    return mock


def make_company(
    *,
    name: str,
    tax_number: str,
    role: CompanyType,
    address: Address | None = None,
    contact: Contact | None = None,
) -> Company:
    return Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name=name,
        tax_number=tax_number,
        description=None,

        address=address,
        contact=contact,
        bank_account=None,

        role=role,
        tags=set(),
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )


# =====================
# FIXTURES
# =====================

@pytest.fixture
def repo():
    return InMemoryCompanyRepository()


@pytest.fixture
def provider(repo):
    return CompositeCompanyCandidateProvider([
        NameCandidateProvider(repo),
        StreetCandidateProvider(repo),
        ExactNipCandidateProvider(repo),
        PhoneCandidateProvider(repo),
        EmailCandidateProvider(repo),
        BankAccountCandidateProvider(repo),
    ])


@pytest.fixture
def orchestrator(repo, provider):
    return CompanyEvaluateOrchestrator(
        company_repo=repo,
        candidate_provider=provider,
        llm_company_resolver=dummy_LLM(),
    )
# =====================
# TESTS
# =====================

def evaluate(orchestrator, input_, mode=EvaluateMode.NORMAL):
    return orchestrator.evaluate(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        input_=input_,
        mode=mode,
    )



def test_resolve_no_candidates_creates_company(repo, orchestrator):
    input_ = CompanyInput(
        name="ACME Sp. z o.o.",
        tax_number="1234567890",
        street="Testowa 1",
        city="Kraków",
        zip_code="30-001",
        country="PL",
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state="małopolska",
    )

    company = evaluate(orchestrator, input_)

    assert repo.exists(company.id,TEST_ORG_ID)

def test_single_candidate_updates_when_input_better(repo, orchestrator):
    existing = make_company(
        name="ACME",
        tax_number="1234567890",
        role=CompanyType.SELLER,
        address=Address("", "", "", ""),
        contact=Contact(None, None),
    )
    repo.add(existing)

    input_ = CompanyInput(
        name="ACME Spółka z o.o.",
        tax_number="1234567890",
        street="Testowa 1",
        city="Kraków",
        zip_code="30-001",
        country="PL",
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state=None,
    )

    company = evaluate(orchestrator, input_)

    assert company.address.street == "Testowa 1"

def test_multiple_candidates_strong_match_wins(repo, orchestrator):
    good = make_company(
        name="ACME Sp. z o.o.",
        tax_number="1111111111",
        role=CompanyType.SELLER,
        address=Address("Testowa 1", "Kraków", "30-001", "PL"),
    )

    bad = make_company(
        name="ACM",
        tax_number="2222222222",
        role=CompanyType.SELLER,
        address=Address("", "", "", ""),
    )

    repo.add(good)
    repo.add(bad)

    input_ = CompanyInput(
        name="ACME Spółka z o.o.",
        tax_number=None,
        street="Testowa 1",
        city="Kraków",
        zip_code="30-001",
        country="PL",
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state=None,
    )

    company = evaluate(orchestrator, input_)

    assert company.id == good.id


def test_create_company_without_tax_number_creates_placeholder(repo, orchestrator):
    input_ = CompanyInput(
        name="No Nip Corp",
        tax_number=None,
        street=None,
        city=None,
        zip_code=None,
        country=None,
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state=None,
    )

    company = evaluate(orchestrator, input_)

    assert company.tax_number.startswith("TMP-")

def test_evaluate_prefers_own_over_seller(repo, orchestrator):
    own = make_company(
        name="Remontivo Sp. z o.o.",
        tax_number="6762680195",
        role=CompanyType.OWN,
        address=Address("Rynek Główny 28", "Kraków", "31-010", "PL"),
    )

    seller = make_company(
        name="Remontivo Spółka",
        tax_number="9999999999",
        role=CompanyType.SELLER,
        address=Address("Rynek Główny 28", "Kraków", "31-010", "PL"),
    )

    repo.add(own)
    repo.add(seller)

    input_ = CompanyInput(
        name="REMONTIVO SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ",
        tax_number=None,
        street="Rynek Główny 28",
        city="Kraków",
        zip_code="31-010",
        country="PL",
        phone_number=None,
        email=None,
        bank_account=None,
        role="Buyer",
        state=None,
    )

    company = evaluate(orchestrator, input_)

    assert company.id == own.id


def test_evaluate_best_scoring_candidate_wins_when_no_own(
    repo: InMemoryCompanyRepository,
    orchestrator: CompanyEvaluateOrchestrator,
):
    good = Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="ACME Sp. z o.o.",
        tax_number="1111111111",
        description=None,

        address=Address("Testowa 1", "Kraków", "30-001", "PL"),
        contact=Contact(None, None),
        bank_account=None,

        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

    bad = Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="ACM",
        tax_number="2222222222",
        description=None,

        address=Address("", "", "", ""),
        contact=Contact(None, None),
        bank_account=None,

        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

    repo.add(good)
    repo.add(bad)

    input_ = CompanyInput(
        name="ACME Spółka z o.o.",
        tax_number=None,
        street="Testowa 1",
        city="Kraków",
        zip_code="30-001",
        country="PL",
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state=None,
    )

    company = orchestrator.evaluate(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        input_=input_,
    )

    assert company.id == good.id


def test_evaluate_creates_company_when_no_candidates(
    repo: InMemoryCompanyRepository,
    orchestrator: CompanyEvaluateOrchestrator,
):
    input_ = CompanyInput(
        name="New Company",
        tax_number=None,
        street=None,
        city=None,
        zip_code=None,
        country=None,
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state=None,
    )

    company = orchestrator.evaluate(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        input_=input_,
    )

    assert company is not None
    assert repo.exists(company.id,TEST_ORG_ID)


def test_soft_update_updates_only_better_fields(orchestrator,repo):
    company = make_company(
        name="ACME Sp. z o.o.",
        tax_number="1234567890",
        role=CompanyType.SELLER,
        address=Address("", "", "", ""),
        contact=Contact(None, None),
    )
    repo.add(company)
    input_ = CompanyInput(
        name="ACME Sp. z o.o.",
        tax_number="1234567890",
        street="Rynek 1",
        city=None,
        zip_code=None,
        country=None,
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state=None,
    )

    updated = orchestrator._maybe_update(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        company=company,
        input_=input_,
        mode=EvaluateMode.NORMAL,
    )

    assert updated.address.street == "Rynek 1"
    assert updated.name == company.name


def test_full_update_replaces_all_fields(orchestrator: CompanyEvaluateOrchestrator,repo):
    company = Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="ACM",
        tax_number="TMP-123",
        description=None,

        address=Address("", "", "", ""),
        contact=Contact(None, None),
        bank_account=None,

        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

    repo.add(company)

    input_ = CompanyInput(
        name="ACME Sp. z o.o.",
        tax_number="7352597495",
        street="Rynek 1",
        city="Kraków",
        zip_code="30-001",
        country="PL",
        phone_number="48 123 456 789",
        email="biuro@acme.pl",
        bank_account="PL121050123456789012345678",
        role="Seller",
        state=None,
    )

    updated = orchestrator._maybe_update(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        company=company,
        input_=input_,
        mode=EvaluateMode.NORMAL,
    )

    assert updated.tax_number == "7352597495"
    assert updated.address.city == "Kraków"
    assert updated.contact.email == "biuro@acme.pl"



def test_does_not_overwrite_good_data_with_bad(orchestrator: CompanyEvaluateOrchestrator):
    company = Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="ACME",
        tax_number="1234567890",
        description=None,

        address=None,
        contact=Contact(None, "biuro@acme.pl"),
        bank_account=None,

        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

    input_ = CompanyInput(
        name=None,
        tax_number="1234567890",
        street=None,
        city=None,
        zip_code=None,
        country=None,
        phone_number=None,
        email="test@",  # ❌ gorszy email
        bank_account=None,
        role="Seller",
        state=None,
    )

    updated = orchestrator._maybe_update(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        company=company,
        input_=input_,
        mode=EvaluateMode.NORMAL,
    )

    assert updated.contact.email == "biuro@acme.pl"


def test_candidate_found_never_creates_new_company(
    repo: InMemoryCompanyRepository,
    orchestrator: CompanyEvaluateOrchestrator,
):
    existing = Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name="ACME",
        tax_number="1234567890",
        description=None,

        address=Address("", "", "", ""),
        contact=Contact(None, None),
        bank_account=None,

        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )
    repo.add(existing)

    input_ = CompanyInput(
        name="ACME",
        tax_number="1234567890",
        street=None,
        city=None,
        zip_code=None,
        country=None,
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state=None,
    )

    company = orchestrator.evaluate(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        input_=input_,
    )

    assert company.id == existing.id
    assert len(repo.list_all(TEST_ORG_ID)) == 1


def test_no_candidates_creates_company_with_placeholder_tax(
    repo: InMemoryCompanyRepository,
    orchestrator: CompanyEvaluateOrchestrator,
):
    input_ = CompanyInput(
        name="NEW COMPANY",
        tax_number=None,
        street=None,
        city=None,
        zip_code=None,
        country=None,
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state=None,
    )

    company = orchestrator.evaluate(
        organization_id=TEST_ORG_ID,
        actor_user_id=TEST_USER_ID,
        input_=input_,
    )

    assert company.tax_number.startswith("TMP-")
    assert len(repo.list_all(TEST_ORG_ID)) == 1


