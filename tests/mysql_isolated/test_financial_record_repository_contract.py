from datetime import date

from contract_costs.common.ids import new_uuid
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.repository.mysql.document_repository import MySQLDocumentRepository
from contract_costs.services.financial_records.review.dto.financial_record_review_query import (
    FinancialRecordReviewQuery,
)
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder


def _assert_same_record(actual, expected):
    assert actual is not None
    assert actual.id == expected.id
    assert actual.organization_id == expected.organization_id
    assert actual.reference == expected.reference
    assert actual.invoice_date == expected.invoice_date
    assert actual.selling_date == expected.selling_date
    assert actual.buyer_id == expected.buyer_id
    assert actual.seller_id == expected.seller_id
    assert actual.payment_method == expected.payment_method
    assert actual.due_date == expected.due_date
    assert actual.paid_date == expected.paid_date
    assert actual.payment_status == expected.payment_status
    assert actual.status == expected.status


def test_financial_record_add_and_get(financial_record_repo_contract):
    org_id = new_uuid()
    record = FinancialRecordBuilder().with_organization_id(org_id).build()

    financial_record_repo_contract.add(record)

    loaded = financial_record_repo_contract.get(
        organization_id=org_id,
        record_id=record.id,
    )
    _assert_same_record(loaded, record)


def test_financial_record_get_isolation_by_org(financial_record_repo_contract):
    org_a = new_uuid()
    org_b = new_uuid()
    record = FinancialRecordBuilder().with_organization_id(org_a).build()
    financial_record_repo_contract.add(record)

    loaded = financial_record_repo_contract.get(
        organization_id=org_b,
        record_id=record.id,
    )
    assert loaded is None


def test_financial_record_get_by_reference_excludes_deleted(financial_record_repo_contract):
    org_id = new_uuid()
    active = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("REF-1")
        .with_status(FinancialRecordStatus.IN_PROGRESS)
        .build()
    )
    deleted = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("REF-1")
        .with_status(FinancialRecordStatus.DELETED)
        .build()
    )
    financial_record_repo_contract.add(active)
    financial_record_repo_contract.add(deleted)

    listed = financial_record_repo_contract.get_by_reference(
        organization_id=org_id,
        reference="REF-1",
    )
    assert [r.id for r in listed] == [active.id]


def test_financial_record_get_unique_record(financial_record_repo_contract):
    org_id = new_uuid()
    seller_id = new_uuid()
    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("UNIQ-1")
        .with_seller_id(seller_id)
        .build()
    )
    financial_record_repo_contract.add(record)

    loaded = financial_record_repo_contract.get_unique_record(
        organization_id=org_id,
        reference="UNIQ-1",
        seller_id=seller_id,
    )
    _assert_same_record(loaded, record)


def test_financial_record_get_for_assignment_by_status(financial_record_repo_contract):
    org_id = new_uuid()
    target = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.NEW_COST)
        .build()
    )
    other = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.PROCESSED)
        .build()
    )
    financial_record_repo_contract.add(target)
    financial_record_repo_contract.add(other)

    listed = financial_record_repo_contract.get_for_assignment(
        organization_id=org_id,
        status=FinancialRecordStatus.NEW_COST,
    )
    assert [r.id for r in listed] == [target.id]


def test_financial_record_list_for_review_filters_and_sorts(financial_record_repo_contract):
    org_id = new_uuid()
    older = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.PROCESSED)
        .with_invoice_date(date(2026, 1, 1))
        .build()
    )
    newer = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.PROCESSED)
        .with_invoice_date(date(2026, 2, 1))
        .build()
    )
    deleted = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.DELETED)
        .with_invoice_date(date(2026, 3, 1))
        .build()
    )
    financial_record_repo_contract.add(older)
    financial_record_repo_contract.add(newer)
    financial_record_repo_contract.add(deleted)

    query = FinancialRecordReviewQuery(
        organization_id=org_id,
        actor_user_id=new_uuid(),
    )
    listed = financial_record_repo_contract.list_for_review(
        organization_id=org_id,
        query=query,
    )
    listed_ids = [r.id for r in listed]
    assert deleted.id not in listed_ids
    assert listed_ids[0] == newer.id
    assert listed_ids[1] == older.id


def test_financial_record_exists_list_all_and_list_by_seller(financial_record_repo_contract):
    org_id = new_uuid()
    seller_a = new_uuid()
    seller_b = new_uuid()
    r1 = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_seller_id(seller_a)
        .build()
    )
    r2 = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_seller_id(seller_b)
        .build()
    )
    financial_record_repo_contract.add(r1)
    financial_record_repo_contract.add(r2)

    assert financial_record_repo_contract.exists(organization_id=org_id, record_id=r1.id) is True
    assert financial_record_repo_contract.exists(organization_id=new_uuid(), record_id=r1.id) is False
    assert {r.id for r in financial_record_repo_contract.list_all(organization_id=org_id)} == {r1.id, r2.id}
    assert [r.id for r in financial_record_repo_contract.list_by_seller_id(organization_id=org_id, seller_id=seller_a)] == [r1.id]


def test_financial_record_has_documents(financial_record_repo_contract):
    org_id = new_uuid()
    record = FinancialRecordBuilder().with_organization_id(org_id).build()
    financial_record_repo_contract.add(record)

    if financial_record_repo_contract.__class__.__name__.startswith("MySQL"):
        doc_repo = MySQLDocumentRepository(connection=financial_record_repo_contract._connection)
        doc = (
            DocumentBuilder()
            .with_organization_id(org_id)
            .with_financial_record_id(record.id)
            .build()
        )
        doc_repo.add(doc)
    else:
        record.documents = [DocumentBuilder().with_organization_id(org_id).build()]
        financial_record_repo_contract.update(record)

    assert financial_record_repo_contract.has_documents(
        organization_id=org_id,
        record_id=record.id,
    ) is True


def test_financial_record_get_record_dates_prefers_selling_date(financial_record_repo_contract):
    org_id = new_uuid()
    with_selling = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_invoice_date(date(2026, 2, 1))
        .with_selling_date(date(2026, 1, 31))
        .build()
    )
    invoice_only = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_invoice_date(date(2026, 3, 1))
        .with_selling_date(None)
        .build()
    )
    other_org = FinancialRecordBuilder().with_organization_id(new_uuid()).build()
    for record in (with_selling, invoice_only, other_org):
        financial_record_repo_contract.add(record)

    dates = financial_record_repo_contract.get_record_dates(
        organization_id=org_id,
        record_ids=[with_selling.id, invoice_only.id, other_org.id],
    )

    assert dates == {
        with_selling.id: date(2026, 1, 31),
        invoice_only.id: date(2026, 3, 1),
    }
    assert financial_record_repo_contract.get_record_dates(organization_id=org_id, record_ids=[]) == {}
