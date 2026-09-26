from dataclasses import replace
from datetime import date, timedelta
from uuid import uuid4

from contract_costs.common.time import utc_now
from contract_costs.services.documents.query.list_documents_query_service import (
    ListDocumentsQueryService,
)
from contract_costs.services.documents.query.list_docuemnts_query_command import (
    ListDocumentsQueryCommand,
)
from tests.builders.document_builder import DocumentBuilder


class StubDocumentRepository:
    def __init__(self, documents):
        self._documents = documents

    def list_filtered(self, **kwargs):
        return self._documents


class StubUow:
    def __init__(self, documents):
        self.documents = documents


def test_execute_sorts_documents_desc_and_maps_fields():
    organization_id = uuid4()
    actor_user_id = uuid4()
    now = utc_now()

    older = replace(
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_file_path(r"C:\docs\older.pdf")
        .build(),
        created_at=now - timedelta(days=1),
    )
    newer = replace(
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_file_path("/var/newer.pdf")
        .with_parsed_payload({"ok": True})
        .with_financial_record_id(uuid4())
        .build(),
        created_at=now,
    )

    repo = StubDocumentRepository([older, newer])
    service = ListDocumentsQueryService()

    result = service.execute(
        action=ListDocumentsQueryCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            has_payload=None,
            has_record=None,
            source=None,
        ),
        uow=StubUow(repo),
    )

    assert [row.document_id for row in result] == [newer.id, older.id]
    assert result[0].file_name == "newer.pdf"
    assert result[1].file_name == "older.pdf"
    assert result[0].has_payload is True
    assert result[0].has_record is True


def test_extract_unknown_values_for_missing_path_or_types():
    organization_id = uuid4()
    actor_user_id = uuid4()
    document = replace(
        DocumentBuilder()
        .with_organization_id(organization_id)
        .build(),
        file_path=None,
        document_source=None,
        document_type=None,
    )

    repo = StubDocumentRepository([document])
    service = ListDocumentsQueryService()

    result = service.execute(
        action=ListDocumentsQueryCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            has_payload=None,
            has_record=None,
            source=None,
        ),
        uow=StubUow(repo),
    )

    assert result[0].file_name == "unknown"
    assert result[0].document_source == "unknown"
    assert result[0].document_type == "unknown"


def _list(documents, organization_id):
    return ListDocumentsQueryService().execute(
        action=ListDocumentsQueryCommand(
            organization_id=organization_id,
            actor_user_id=uuid4(),
        ),
        uow=StubUow(StubDocumentRepository(documents)),
    )


def test_maps_parties_and_invoice_date_from_payload():
    organization_id = uuid4()
    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_parsed_payload(
            {
                "seller": {"name": "Hurtownia ABC", "tax_number": "1234567890"},
                "buyer": {"name": "Nasza Firma", "tax_number": "9876543210"},
                "record": {"invoice_date": "2026-09-15"},
            }
        )
        .build()
    )

    [row] = _list([document], organization_id)

    assert row.seller_name == "Hurtownia ABC"
    assert row.buyer_name == "Nasza Firma"
    assert row.buyer_nip == "9876543210"
    assert row.invoice_date == date(2026, 9, 15)


def test_parties_are_none_without_payload_or_with_broken_payload():
    organization_id = uuid4()
    without_payload = DocumentBuilder().with_organization_id(organization_id).build()
    broken = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_parsed_payload(
            {"seller": "x", "buyer": None, "record": {"invoice_date": "bez daty"}}
        )
        .build()
    )

    for row in _list([without_payload, broken], organization_id):
        assert row.seller_name is None
        assert row.buyer_name is None
        assert row.buyer_nip is None
        assert row.invoice_date is None


def test_documents_imported_in_same_second_have_stable_order():
    organization_id = uuid4()
    now = utc_now()
    documents = [
        replace(
            DocumentBuilder()
            .with_organization_id(organization_id)
            .build(),
            created_at=now,
            document_number=number,
        )
        for number in ["FV/2", "FV/3", "FV/1"]
    ]

    first = [row.document_number for row in _list(documents, organization_id)]
    second = [row.document_number for row in _list(list(reversed(documents)), organization_id)]

    assert first == second == ["FV/3", "FV/2", "FV/1"]
