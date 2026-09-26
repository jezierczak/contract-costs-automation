"""
Regresje dopasowania firm z prawdziwych importów.

SIG / SIGNAL (2026-09-26): faktura KSeF od SIGNAL z NIP-em spoza bazy
została dopasowana do istniejącej SIG sp. z o.o., bo "SIG" zawiera się
w "SIGNAL" (NameCandidateProvider), a obecność jakiegokolwiek kandydata
blokuje utworzenie nowej firmy.
"""

from dataclasses import replace

from contract_costs.common.ids import new_uuid
from contract_costs.model.company import CompanyType
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.companies.providers.composite import CompositeCompanyCandidateProvider
from contract_costs.services.companies.providers.excact_nip import ExactNipCandidateProvider
from contract_costs.services.companies.providers.name import NameCandidateProvider
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from tests.builders.company_builder import CompanyBuilder

SIG_NIP = "5251234560"
SIGNAL_NIP = "7812345678"


def build_orchestrator() -> CompanyEvaluateOrchestrator:
    return CompanyEvaluateOrchestrator(
        CompositeCompanyCandidateProvider([
            ExactNipCandidateProvider(),
            NameCandidateProvider(),
        ]),
        llm_company_resolver=None,
    )


def signal_input() -> CompanyInput:
    return CompanyInput(
        name="SIGNAL SP. Z O.O.",
        tax_number=SIGNAL_NIP,
        state=None,
        street="ul. Przemysłowa 12",
        zip_code="61-001",
        city="Poznań",
        phone_number="+48 600 100 200",
        email="biuro@signal.pl",
        country="PL",
        bank_account=None,
        role=CompanyType.SELLER.value,
    )


def test_different_nip_is_not_matched_by_name_substring(company_repo, uow):
    org_id = new_uuid()
    sig = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("SIG SP. Z O.O.")
        .with_tax_number(SIG_NIP)
        .with_address(street="ul. Leśna 1", city="Warszawa", zip_code="00-001", country="PL")
        .build()
    )
    company_repo.add(sig)

    result = build_orchestrator().evaluate(
        uow=uow,
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=signal_input(),
    )

    assert result.id != sig.id
    assert result.tax_number == SIGNAL_NIP
    assert result.name == "SIGNAL SP. Z O.O."


def test_existing_company_keeps_its_nip_and_name(company_repo, uow):
    org_id = new_uuid()
    sig = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_name("SIG SP. Z O.O.")
        .with_tax_number(SIG_NIP)
        .build()
    )
    company_repo.add(sig)

    # KSeF prawie zawsze podaje rachunek - pełne dane włączają pełną aktualizację
    build_orchestrator().evaluate(
        uow=uow,
        organization_id=org_id,
        actor_user_id=new_uuid(),
        input_=replace(signal_input(), bank_account="PL61109010140000071219812874"),
    )

    stored = company_repo.get(sig.id, org_id)
    assert stored.tax_number == SIG_NIP
    assert stored.name == "SIG SP. Z O.O."
