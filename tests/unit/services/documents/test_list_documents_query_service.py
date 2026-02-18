from dataclasses import replace
from datetime import timedelta
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
