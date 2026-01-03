from unittest import skip
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from contract_costs.infrastructure.openai_invoice_client import OpenAIInvoiceClient
from contract_costs.model.company import Company, Address, Contact, CompanyType
from contract_costs.repository.inmemory.company_repository import InMemoryCompanyRepository
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.companies.providers.address import AddressCandidateProvider
from contract_costs.services.companies.providers.bank import BankAccountCandidateProvider
from contract_costs.services.companies.providers.composite import CompositeCompanyCandidateProvider
from contract_costs.services.companies.providers.email import EmailCandidateProvider
from contract_costs.services.companies.providers.excact_nip import ExactNipCandidateProvider
from contract_costs.services.companies.providers.name import NameCandidateProvider
from contract_costs.services.companies.providers.phone import PhoneCandidateProvider
from contract_costs.services.invoices.dto.parse import CompanyInput



def dummy_LLM():
    mock = MagicMock(OpenAIInvoiceClient)
    mock.resolve_company.return_value = None
    return mock


@pytest.fixture
def repo():
    return InMemoryCompanyRepository()

@pytest.fixture
def provider(repo: InMemoryCompanyRepository):
    return CompositeCompanyCandidateProvider([
        NameCandidateProvider(repo),
        AddressCandidateProvider(repo),
        ExactNipCandidateProvider(repo),
        PhoneCandidateProvider(repo),
        EmailCandidateProvider(repo),
        BankAccountCandidateProvider(repo)
    ])

@pytest.fixture
def orchestrator(repo: InMemoryCompanyRepository, provider: CompositeCompanyCandidateProvider):
    return CompanyEvaluateOrchestrator(
        company_repo=repo,
        candidate_provider=provider,
        llm_company_resolver=dummy_LLM(),
    )

def test_resolve_no_candidates_creates_company(repo: InMemoryCompanyRepository,orchestrator: CompanyEvaluateOrchestrator):
    # provider = CompositeCompanyCandidateProvider([])
    # orchestrator = CompanyEvaluateOrchestrator(
    #     candidate_provider=provider,
    #     company_repo=repo,
    #     llm_company_resolver=dummy_LLM(),
    # )

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
        state="małopolska"
    )

    company = orchestrator.evaluate(input_)

    assert company.id in repo._companies

def test_single_candidate_updates_when_input_better(repo: InMemoryCompanyRepository,orchestrator: CompanyEvaluateOrchestrator):

    existing = Company(
        id=uuid4(),
        name="ACME",
        tax_number="1234567890",
        address=Address("", "", "", ""),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
    )
    repo.add(existing)
    #
    # provider = ExactNipCandidateProvider(repo)
    #
    # orchestrator = CompanyEvaluateOrchestrator(
    #     candidate_provider=provider,
    #     company_repo=repo,
    #     llm_company_resolver=dummy_LLM(),
    # )

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
        state="małopolska"
    )

    company = orchestrator.evaluate(input_)

    assert company.address.street == "Testowa 1"


def test_multiple_candidates_strong_match_wins(repo: InMemoryCompanyRepository,orchestrator: CompanyEvaluateOrchestrator):

    good = Company(
        id=uuid4(),
        name="ACME Sp. z o.o.",
        tax_number="1111111111",
        address=Address("Testowa 1", "Kraków", "30-001", "PL"),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
    )

    bad = Company(
        id=uuid4(),
        name="ACM",
        tax_number="2222222222",
        address=Address("", "", "", ""),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
    )

    repo.add(good)
    repo.add(bad)

    # provider = CompositeCompanyCandidateProvider([
    #     ExactNipCandidateProvider(repo),
    #     NameCandidateProvider(repo),
    #     BankAccountCandidateProvider(repo),
    #     EmailCandidateProvider(repo),
    #     PhoneCandidateProvider(repo),
    #     AddressCandidateProvider(repo),
    # ])
    #
    # orchestrator = CompanyEvaluateOrchestrator(
    #     candidate_provider=provider,
    #     company_repo=repo,
    #     llm_company_resolver=dummy_LLM(),
    # )

    input_ = CompanyInput(
        name="ACME Spółka z o.o.",
        tax_number="",
        street="Testowa 1",
        city="Kraków",
        zip_code="30-001",
        country="PL",
        phone_number=None,
        email=None,
        bank_account=None,
        role="Seller",
        state="małopolska"
    )

    company = orchestrator.evaluate(input_)

    assert company.id == good.id

def test_create_company_without_tax_number_creates_placeholder(repo: InMemoryCompanyRepository,orchestrator: CompanyEvaluateOrchestrator):

    # provider = CompositeCompanyCandidateProvider([])
    # orchestrator = CompanyEvaluateOrchestrator(
    #     candidate_provider=provider,
    #     company_repo=repo,
    #     llm_company_resolver=dummy_LLM(),
    # )

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

    company = orchestrator.evaluate(input_)

    assert company.tax_number.startswith("TMP-")
    assert company.id is not None


def test_evaluate_prefers_own_over_seller(repo:InMemoryCompanyRepository,orchestrator: CompanyEvaluateOrchestrator):

    own = Company(
        id=uuid4(),
        name="Remontivo Sp. z o.o.",
        tax_number="6762680195",
        address=Address("Rynek Główny 28", "Kraków", "31-010", "PL"),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.OWN,
        tags=set(),
        is_active=True,
        description=None,
    )

    seller = Company(
        id=uuid4(),
        name="Remontivo Spółka",
        tax_number="9999999999",
        address=Address("Rynek Główny 28", "Kraków", "31-010", "PL"),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
    )

    repo.add(own)
    repo.add(seller)

    # provider = CompositeCompanyCandidateProvider([
    #     NameCandidateProvider(repo),
    #     AddressCandidateProvider(repo),
    # ])
    #
    # orchestrator = CompanyEvaluateOrchestrator(
    #     company_repo=repo,
    #     candidate_provider=provider,
    #     llm_company_resolver=dummy_LLM(),
    # )

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

    company = orchestrator.evaluate(input_)

    assert company.id == own.id


def test_evaluate_best_scoring_candidate_wins_when_no_own(repo: InMemoryCompanyRepository,orchestrator: CompanyEvaluateOrchestrator):

    good = Company(
        id=uuid4(),
        name="ACME Sp. z o.o.",
        tax_number="1111111111",
        address=Address("Testowa 1", "Kraków", "30-001", "PL"),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
    )

    bad = Company(
        id=uuid4(),
        name="ACM",
        tax_number="2222222222",
        address=Address("", "", "", ""),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
    )

    repo.add(good)
    repo.add(bad)

    # provider = CompositeCompanyCandidateProvider([
    #     NameCandidateProvider(repo),
    #     AddressCandidateProvider(repo),
    # ])
    #
    # orchestrator = CompanyEvaluateOrchestrator(
    #     company_repo=repo,
    #     candidate_provider=provider,
    #     llm_company_resolver=dummy_LLM(),
    # )

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

    company = orchestrator.evaluate(input_)

    assert company.id == good.id


def test_evaluate_creates_company_when_no_candidates(repo: InMemoryCompanyRepository, orchestrator: CompanyEvaluateOrchestrator):

    # provider = CompositeCompanyCandidateProvider([])
    #
    # orchestrator = CompanyEvaluateOrchestrator(
    #     company_repo=repo,
    #     candidate_provider=provider,
    #     llm_company_resolver=dummy_LLM(),
    # )

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

    company = orchestrator.evaluate(input_)

    assert company is not None
    assert repo.exists(company.id)


def test_soft_update_updates_only_better_fields(orchestrator: CompanyEvaluateOrchestrator):



    company = Company(
        id=uuid4(),
        name="ACME Sp. z o.o.",
        tax_number="1234567890",
        address=Address("", "", "", ""),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
    )

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

    updated = orchestrator._maybe_update(company, input_)

    assert updated.address.street == "Rynek 1"
    assert updated.name == "ACME Sp. z o.o."


def test_full_update_replaces_all_fields(orchestrator: CompanyEvaluateOrchestrator):
    company = Company(
        id=uuid4(),
        name="ACM",
        tax_number="TMP-123",
        address=Address("", "", "", ""),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
    )

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

    updated = orchestrator._maybe_update(company, input_)

    assert updated.tax_number == "7352597495"
    assert updated.address.city == "Kraków"
    assert updated.contact.email == "biuro@acme.pl"


def test_does_not_overwrite_good_data_with_bad(orchestrator: CompanyEvaluateOrchestrator):
    company = Company(
        id=uuid4(),
        name="ACME",
        tax_number="1234567890",
        address=None,
        contact=Contact(None, "biuro@acme.pl"),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
    )

    input_ = CompanyInput(
        name=None,
        tax_number="1234567890",
        street=None,
        city=None,
        zip_code=None,
        country=None,
        phone_number=None,
        email="test@",
        bank_account=None,
        role="Seller",
        state=None,
    )

    updated = orchestrator._maybe_update(company, input_)

    assert updated.contact.email == "biuro@acme.pl"

def test_candidate_found_never_creates_new_company(repo: InMemoryCompanyRepository, orchestrator: CompanyEvaluateOrchestrator):

    existing = Company(
        id=uuid4(),
        name="ACME",
        tax_number="1234567890",
        address=Address("", "", "", ""),
        contact=Contact(None, None),
        bank_account=None,
        role=CompanyType.SELLER,
        tags=set(),
        is_active=True,
        description=None,
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

    company = orchestrator.evaluate(input_)

    assert company.id == existing.id
    assert len(repo.list_all()) == 1

def test_no_candidates_creates_company_with_placeholder_tax(repo: InMemoryCompanyRepository,orchestrator: CompanyEvaluateOrchestrator):

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

    company = orchestrator.evaluate(input_)

    assert company.tax_number.startswith("TMP-")
    assert len(repo.list_all()) == 1

