from uuid import uuid4

from contract_costs.repository.inmemory.document_repository import InMemoryDocumentRepository
from tests.builders.document_builder import DocumentBuilder


def test_inmemory_document_repo_is_isolated_by_organization():
    repo = InMemoryDocumentRepository()
    org_a = uuid4()
    org_b = uuid4()

    doc = DocumentBuilder().with_organization_id(org_a).build()
    repo.add(doc)

    assert repo.get(organization_id=org_a, document_id=doc.id) is not None
    assert repo.get(organization_id=org_b, document_id=doc.id) is None


def test_inmemory_document_repo_attach_to_record_is_idempotent():
    repo = InMemoryDocumentRepository()
    org_id = uuid4()
    first_record_id = uuid4()
    second_record_id = uuid4()

    doc = DocumentBuilder().with_organization_id(org_id).build()
    repo.add(doc)

    repo.attach_to_record(
        organization_id=org_id,
        document_id=doc.id,
        record_id=first_record_id,
    )
    repo.attach_to_record(
        organization_id=org_id,
        document_id=doc.id,
        record_id=second_record_id,
    )

    updated = repo.get(organization_id=org_id, document_id=doc.id)
    assert updated is not None
    assert updated.financial_record_id == first_record_id
