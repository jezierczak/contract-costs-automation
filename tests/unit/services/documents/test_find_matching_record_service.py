from datetime import date
from decimal import Decimal
from uuid import uuid4

from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentSource, ScoringResult
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.services.documents.scoring.document_decision import DocumentDecision
from contract_costs.services.documents.scoring.document_decision_service import DocumentDecisionService
from contract_costs.services.documents.scoring.find_matching_record_service import (
    FindMatchingRecordService,
    MatchReason,
)
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import (
    DocumentParseNormalizer,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder

ORG = uuid4()
SELLER_NIP = "5261009959"
OWN_NIP = "5532452113"
OTHER_OWN_NIP = "6792740424"
DOC_DATE = date(2026, 9, 10)


def _company(uow, nip, role=CompanyType.SUPPLIER):
    company = CompanyBuilder().with_organization_id(ORG).with_tax_number(nip).with_role(role).build()
    uow.companies.add(company)
    return company


def _record(uow, *, seller, buyer, reference="FV/OLD", gross="123.00", item="Kabel",
            invoice_date=DOC_DATE, status=None):
    builder = (
        FinancialRecordBuilder()
        .with_organization_id(ORG)
        .with_seller_id(seller.id)
        .with_buyer_id(buyer.id)
        .with_reference(reference)
        .with_invoice_date(invoice_date)
    )
    if status is not None:
        builder = builder.with_status(status)
    record = builder.build()
    uow.financial_records.add(record)
    uow.financial_record_lines.add(
        organization_id=ORG,
        line=(
            FinancialRecordLineBuilder()
            .with_organization_id(ORG)
            .with_financial_record_id(record.id)
            .with_item_name(item)
            .with_quantity(Decimal("1"))
            .with_amount(Amount(
                value=Decimal(gross),
                input_type=AmountInputType.GROSS,
                vat_rate=VatRate.VAT_23,
                tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
            ))
            .build()
        ),
    )
    return record


def _document(*, reference="FV/1/2026", seller_nip=SELLER_NIP, buyer_nip=OWN_NIP, gross="123.00",
              item="Kabel", source=DocumentSource.PDF, score=90):
    payload = {
        "record": {"reference": reference, "invoice_date": DOC_DATE.isoformat()},
        "seller": {"name": "Hurtownia", "tax_number": seller_nip},
        "buyer": {"name": "My", "tax_number": buyer_nip},
        "lines": [{
            "item_name": item,
            "quantity": "1",
            "amount": {"value": gross, "input_type": "gross", "vat_rate": "23"},
        }],
    }
    return (
        DocumentBuilder()
        .with_organization_id(ORG)
        .with_document_source(source)
        .with_document_number(reference)
        .with_seller_nip(seller_nip)
        .with_parsed_payload(payload)
        .with_scoring(ScoringResult(score=score, breakdown={}))
        .build()
    )


def _matching():
    return FindMatchingRecordService(document_parse_normalizer=DocumentParseNormalizer())


def _reasons(result):
    return {m.record.id: m.reasons for m in result.matches}


# ============================================================
# MATCHING
# ============================================================

def test_strict_match_by_reference_and_seller(uow):
    seller = _company(uow, SELLER_NIP)
    own = _company(uow, OWN_NIP, CompanyType.OWN)
    record = _record(uow, seller=seller, buyer=own, reference="FV/1/2026", gross="999.00", item="Inne")

    result = _matching().find(document=_document(), uow=uow)

    assert [m.record.id for m in result.strict] == [record.id]
    assert result.seller.id == seller.id and result.buyer.id == own.id


def test_candidates_carry_reasons(uow):
    seller = _company(uow, SELLER_NIP)
    own = _company(uow, OWN_NIP, CompanyType.OWN)
    record = _record(uow, seller=seller, buyer=own)

    result = _matching().find(document=_document(), uow=uow)

    assert result.strict == []
    assert _reasons(result)[record.id] >= {MatchReason.TOTAL, MatchReason.NAMES}


def test_candidates_of_another_buyer_are_skipped(uow):
    seller = _company(uow, SELLER_NIP)
    _company(uow, OWN_NIP, CompanyType.OWN)
    other_own = _company(uow, OTHER_OWN_NIP, CompanyType.OWN)
    _record(uow, seller=seller, buyer=other_own)

    assert _matching().find(document=_document(), uow=uow).matches == []


def test_amount_only_match_outside_window_is_skipped(uow):
    seller = _company(uow, SELLER_NIP)
    own = _company(uow, OWN_NIP, CompanyType.OWN)
    _record(uow, seller=seller, buyer=own, item="Coś innego", invoice_date=date(2025, 1, 10))

    assert _matching().find(document=_document(), uow=uow).matches == []


def test_deleted_records_are_skipped(uow):
    seller = _company(uow, SELLER_NIP)
    own = _company(uow, OWN_NIP, CompanyType.OWN)
    _record(uow, seller=seller, buyer=own, reference="FV/1/2026", status=FinancialRecordStatus.DELETED)

    assert _matching().find(document=_document(), uow=uow).matches == []


def test_unknown_seller_gives_no_matches(uow):
    result = _matching().find(document=_document(seller_nip="1234567890"), uow=uow)

    assert result.seller is None
    assert result.matches == []


# ============================================================
# DECISION
# ============================================================

def _decide(uow, document):
    return DocumentDecisionService(matching_service=_matching()).decide(document=document, uow=uow)


def test_single_strict_match_is_attached(uow):
    seller = _company(uow, SELLER_NIP)
    own = _company(uow, OWN_NIP, CompanyType.OWN)
    record = _record(uow, seller=seller, buyer=own, reference="FV/1/2026")

    result = _decide(uow, _document())

    assert result.decision == DocumentDecision.AUTO_ATTACH
    assert result.record_id == record.id


def test_known_parties_without_matches_create_record(uow):
    _company(uow, SELLER_NIP)
    _company(uow, OWN_NIP, CompanyType.OWN)

    assert _decide(uow, _document()).decision == DocumentDecision.AUTO_CREATE


def test_new_seller_with_valid_nip_creates_record(uow):
    _company(uow, OWN_NIP, CompanyType.OWN)

    assert _decide(uow, _document()).decision == DocumentDecision.AUTO_CREATE


def test_candidates_need_manual_decision(uow):
    seller = _company(uow, SELLER_NIP)
    own = _company(uow, OWN_NIP, CompanyType.OWN)
    _record(uow, seller=seller, buyer=own)

    assert _decide(uow, _document()).decision == DocumentDecision.MANUAL


def test_unknown_seller_never_creates_record(uow):
    _company(uow, OWN_NIP, CompanyType.OWN)

    assert _decide(uow, _document(seller_nip="1234567890")).decision == DocumentDecision.MANUAL


def test_unknown_buyer_never_creates_record(uow):
    _company(uow, SELLER_NIP)

    assert _decide(uow, _document(buyer_nip=None)).decision == DocumentDecision.MANUAL


def test_low_score_ocr_is_manual_but_ksef_is_not(uow):
    _company(uow, SELLER_NIP)
    _company(uow, OWN_NIP, CompanyType.OWN)

    assert _decide(uow, _document(score=50)).decision == DocumentDecision.MANUAL
    assert _decide(uow, _document(score=50, source=DocumentSource.KSEF)).decision == DocumentDecision.AUTO_CREATE
