from contract_costs.common.ids import new_uuid
from tests.builders.document_builder import DocumentBuilder


def test_add_and_get_document(document_repo):
    org_id = new_uuid()

    document = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .build()
    )

    document_repo.add(document)

    result = document_repo.get(
        organization_id=org_id,
        document_id=document.id,
    )

    assert result == document


def test_get_isolated_by_organization(document_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    document = (
        DocumentBuilder()
        .with_organization_id(org1)
        .build()
    )

    document_repo.add(document)

    result = document_repo.get(
        organization_id=org2,
        document_id=document.id,
    )

    assert result is None


def test_list_unattached_returns_only_without_record(document_repo):
    org_id = new_uuid()

    doc1 = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .build()
    )

    doc2 = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(new_uuid())
        .build()
    )

    document_repo.add(doc1)
    document_repo.add(doc2)

    result = document_repo.list_unattached(organization_id=org_id)

    assert result == [doc1]


def test_list_by_record_id(document_repo):
    org_id = new_uuid()
    record_id = new_uuid()

    doc = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record_id)
        .build()
    )

    document_repo.add(doc)

    result = document_repo.list_by_record_id(
        organization_id=org_id,
        record_id=record_id,
    )

    assert result == [doc]


def test_attach_to_record_sets_record_id(document_repo):
    org_id = new_uuid()
    record_id = new_uuid()

    doc = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .build()
    )

    document_repo.add(doc)

    document_repo.attach_to_record(
        organization_id=org_id,
        document_id=doc.id,
        record_id=record_id,
    )

    updated = document_repo.get(
        organization_id=org_id,
        document_id=doc.id,
    )

    assert updated.financial_record_id == record_id


def test_attach_does_not_override_existing_record(document_repo):
    org_id = new_uuid()
    record1 = new_uuid()
    record2 = new_uuid()

    doc = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record1)
        .build()
    )

    document_repo.add(doc)

    document_repo.attach_to_record(
        organization_id=org_id,
        document_id=doc.id,
        record_id=record2,
    )

    updated = document_repo.get(
        organization_id=org_id,
        document_id=doc.id,
    )

    assert updated.financial_record_id == record1


def test_delete_document(document_repo):
    org_id = new_uuid()

    doc = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .build()
    )

    document_repo.add(doc)

    document_repo.delete(
        organization_id=org_id,
        document_id=doc.id,
    )

    assert document_repo.get(
        organization_id=org_id,
        document_id=doc.id,
    ) is None


def test_exists_by_hash(document_repo):
    org_id = new_uuid()

    doc = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_file_hash("abc123")
        .build()
    )

    document_repo.add(doc)

    found = document_repo.get_by_hash(
        organization_id=org_id,
        file_hash="abc123",
    )
    assert found is not None
    assert found.id == doc.id

    assert document_repo.get_by_hash(
        organization_id=org_id,
        file_hash="does-not-exist",
    ) is None
