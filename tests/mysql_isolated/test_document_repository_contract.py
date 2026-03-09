from contract_costs.common.ids import new_uuid
from tests.builders.document_builder import DocumentBuilder


def _assert_same_document(actual, expected):
    assert actual is not None
    assert actual.id == expected.id
    assert actual.organization_id == expected.organization_id
    assert actual.financial_record_id == expected.financial_record_id
    assert actual.document_source == expected.document_source
    assert actual.document_type == expected.document_type
    assert actual.document_number == expected.document_number
    assert actual.seller_nip == expected.seller_nip
    assert actual.parsed_payload == expected.parsed_payload
    assert actual.file_hash == expected.file_hash
    assert actual.file_path == expected.file_path
    assert actual.filename == expected.filename
    assert actual.mime_type == expected.mime_type
    assert actual.size == expected.size


def test_document_add_and_get(document_repo_contract):
    org_id = new_uuid()
    doc = DocumentBuilder().with_organization_id(org_id).build()

    document_repo_contract.add(doc)

    loaded = document_repo_contract.get(organization_id=org_id, document_id=doc.id)
    _assert_same_document(loaded, doc)


def test_document_get_is_isolated_by_org(document_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    doc = DocumentBuilder().with_organization_id(org_a).build()
    document_repo_contract.add(doc)

    assert document_repo_contract.get(organization_id=org_b, document_id=doc.id) is None


def test_document_attach_to_record_is_idempotent(document_repo_contract):
    org_id = new_uuid()
    record_a = new_uuid()
    record_b = new_uuid()
    doc = DocumentBuilder().with_organization_id(org_id).build()
    document_repo_contract.add(doc)

    document_repo_contract.attach_to_record(
        organization_id=org_id,
        document_id=doc.id,
        record_id=record_a,
    )
    document_repo_contract.attach_to_record(
        organization_id=org_id,
        document_id=doc.id,
        record_id=record_b,
    )

    loaded = document_repo_contract.get(organization_id=org_id, document_id=doc.id)
    assert loaded is not None
    assert loaded.financial_record_id == record_a


def test_document_list_unattached_returns_only_unassigned(document_repo_contract):
    org_id = new_uuid()
    unattached = DocumentBuilder().with_organization_id(org_id).build()
    attached = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(new_uuid())
        .build()
    )
    document_repo_contract.add(unattached)
    document_repo_contract.add(attached)

    docs = document_repo_contract.list_unattached(organization_id=org_id)
    assert [d.id for d in docs] == [unattached.id]


def test_document_exists_by_hash_scoped_by_org(document_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    file_hash = "same-hash"
    doc = (
        DocumentBuilder()
        .with_organization_id(org_a)
        .with_file_hash(file_hash)
        .build()
    )
    document_repo_contract.add(doc)

    assert document_repo_contract.get_by_hash(organization_id=org_a, file_hash=file_hash) is True
    assert document_repo_contract.get_by_hash(organization_id=org_b, file_hash=file_hash) is False


def test_document_update_delete_and_list_by_record(document_repo_contract):
    org_id = new_uuid()
    record_id = new_uuid()
    doc = DocumentBuilder().with_organization_id(org_id).build()
    document_repo_contract.add(doc)

    doc.file_path = "updated/path.pdf"
    doc.financial_record_id = record_id
    document_repo_contract.update(doc)

    loaded = document_repo_contract.get(organization_id=org_id, document_id=doc.id)
    assert loaded is not None
    assert loaded.file_path == "updated/path.pdf"

    by_record = document_repo_contract.list_by_record_id(
        organization_id=org_id,
        record_id=record_id,
    )
    assert [d.id for d in by_record] == [doc.id]

    document_repo_contract.delete(organization_id=org_id, document_id=doc.id)
    assert document_repo_contract.get(organization_id=org_id, document_id=doc.id) is None


def test_document_list_all_and_filtered(document_repo_contract):
    org_id = new_uuid()
    no_payload = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_parsed_payload(None)
        .with_financial_record_id(None)
        .build()
    )
    with_payload_and_record = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_parsed_payload({"x": 1})
        .with_financial_record_id(new_uuid())
        .build()
    )
    document_repo_contract.add(no_payload)
    document_repo_contract.add(with_payload_and_record)

    all_docs = document_repo_contract.list_all(organization_id=org_id)
    assert {d.id for d in all_docs} == {no_payload.id, with_payload_and_record.id}

    only_payload = document_repo_contract.list_filtered(
        organization_id=org_id,
        has_payload=True,
    )
    assert [d.id for d in only_payload] == [with_payload_and_record.id]

    only_unassigned = document_repo_contract.list_filtered(
        organization_id=org_id,
        has_record=False,
    )
    assert [d.id for d in only_unassigned] == [no_payload.id]
