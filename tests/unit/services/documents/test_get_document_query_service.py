from decimal import Decimal
from uuid import uuid4

from contract_costs.model.company import CompanyType
from contract_costs.services.companies.company_evaluate_orchestrator import CompanyEvaluateOrchestrator
from contract_costs.services.documents.query.dto.get_document_query import GetDocumentQuery
from contract_costs.services.documents.query.get_document_query import GetDocumentQueryService
from contract_costs.services.documents.scoring.find_matching_record_service import FindMatchingRecordService
from contract_costs.services.financial_records.assigment.invoice_sources.normalization.invoice_parser_normalizer import (
    DocumentParseNormalizer,
)
from tests.builders.company_builder import CompanyBuilder
from tests.unit.services.company.test_company_evaluate_orchestrator import FakeCandidateProvider
from tests.unit.services.documents.test_find_matching_record_service import (
    ORG,
    OWN_NIP,
    SELLER_NIP,
    _company,
    _document,
    _record,
)


def _service(suggestions=()):
    provider = FakeCandidateProvider()
    provider.set_candidates(list(suggestions))
    return GetDocumentQueryService(
        matching_service=FindMatchingRecordService(document_parse_normalizer=DocumentParseNormalizer()),
        company_evaluate=CompanyEvaluateOrchestrator(provider, llm_company_resolver=None),
        normalizer=DocumentParseNormalizer(),
    )


def _query(uow, document, service=None):
    uow.documents.add(document)
    return (service or _service()).execute(
        action=GetDocumentQuery(organization_id=ORG, actor_user_id=uuid4(), document_id=document.id),
        uow=uow,
    )


def test_screen_data_has_parties_and_candidates_with_differences(uow):
    seller = _company(uow, SELLER_NIP)
    own = _company(uow, OWN_NIP, CompanyType.OWN)
    record = _record(uow, seller=seller, buyer=own, gross="125.00", item="Kabel")

    dto = _query(uow, _document())

    assert dto.seller.company.id == seller.id
    assert dto.buyer.company.id == own.id
    assert dto.seller.suggestions == []
    assert dto.total_gross == Decimal("123.00")
    [candidate] = dto.candidates
    assert candidate.record_id == record.id
    assert "names" in candidate.reasons
    assert candidate.same_seller and candidate.same_buyer
    assert candidate.total_difference == Decimal("2.00")


def test_unknown_seller_gets_suggestions_and_document_data(uow):
    _company(uow, OWN_NIP, CompanyType.OWN)
    similar = CompanyBuilder().with_organization_id(ORG).with_tax_number("6431668510").with_name("Hurtownia X").build()
    uow.companies.add(similar)

    dto = _query(uow, _document(seller_nip="1234567890"), service=_service(suggestions=[similar]))

    assert dto.seller.company is None
    assert dto.seller.tax_number == "1234567890"
    assert dto.seller.name == "Hurtownia"
    assert [s.id for s in dto.seller.suggestions] == [similar.id]
    assert dto.candidates == []
