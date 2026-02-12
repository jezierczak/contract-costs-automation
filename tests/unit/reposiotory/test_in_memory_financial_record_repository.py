from datetime import date

from contract_costs.common.ids import new_uuid
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.services.financial_records.review.dto.financial_record_review_query import \
    FinancialRecordReviewQuery
from tests.builders.financial_record_builder import FinancialRecordBuilder


def test_add_and_get(financial_record_repo):
    org_id = new_uuid()

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .build()
    )

    financial_record_repo.add(record)

    result = financial_record_repo.get(
        organization_id=org_id,
        record_id=record.id,
    )

    assert result == record

def test_get_isolated_by_org(financial_record_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org1)
        .build()
    )

    financial_record_repo.add(record)

    assert financial_record_repo.get(
        organization_id=org2,
        record_id=record.id,
    ) is None

def test_get_by_reference_ignores_deleted(financial_record_repo):
    org_id = new_uuid()

    active = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("INV-1")
        .build()
    )

    deleted = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("INV-1")
        .with_status(FinancialRecordStatus.DELETED)
        .build()
    )

    financial_record_repo.add(active)
    financial_record_repo.add(deleted)

    result = financial_record_repo.get_by_reference(
        organization_id=org_id,
        reference="INV-1",
    )

    assert result == [active]


def test_get_unique_record(financial_record_repo):
    org_id = new_uuid()
    seller_id = new_uuid()

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("INV-2")
        .with_seller_id(seller_id)
        .build()
    )

    financial_record_repo.add(record)

    result = financial_record_repo.get_unique_record(
        organization_id=org_id,
        reference="INV-2",
        seller_id=seller_id,
    )

    assert result == record

def test_get_for_assignment(financial_record_repo):
    org_id = new_uuid()

    r1 = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.NEW_COST)
        .build()
    )

    r2 = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.PROCESSED)
        .build()
    )

    financial_record_repo.add(r1)
    financial_record_repo.add(r2)

    result = financial_record_repo.get_for_assignment(
        organization_id=org_id,
        status=FinancialRecordStatus.NEW_COST,
    )

    assert result == [r1]


def test_list_for_review_excludes_deleted(financial_record_repo):
    org_id = new_uuid()

    active = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .build()
    )

    deleted = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.DELETED)
        .build()
    )

    financial_record_repo.add(active)
    financial_record_repo.add(deleted)

    query = FinancialRecordReviewQuery()

    result = financial_record_repo.list_for_review(
        organization_id=org_id,
        query=query,
    )

    assert deleted not in result
    assert active in result


def test_list_for_review_only_ready(financial_record_repo):
    org_id = new_uuid()

    processed = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.PROCESSED)
        .build()
    )

    draft = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.DRAFT)
        .build()
    )

    financial_record_repo.add(processed)
    financial_record_repo.add(draft)

    query = FinancialRecordReviewQuery(
        only_ready_for_accountant=True
    )

    result = financial_record_repo.list_for_review(
        organization_id=org_id,
        query=query,
    )

    assert result == [processed]


def test_list_for_review_date_filter(financial_record_repo):
    org_id = new_uuid()

    old = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_invoice_date(date(2024, 1, 1))
        .build()
    )

    new = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_invoice_date(date(2025, 1, 1))
        .build()
    )

    financial_record_repo.add(old)
    financial_record_repo.add(new)

    query = FinancialRecordReviewQuery(
        from_date=date(2024, 6, 1)
    )

    result = financial_record_repo.list_for_review(
        organization_id=org_id,
        query=query,
    )

    assert result == [new]


def test_list_for_review_sorted_desc(financial_record_repo):
    org_id = new_uuid()

    older = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_invoice_date(date(2024, 1, 1))
        .build()
    )

    newer = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_invoice_date(date(2025, 1, 1))
        .build()
    )

    financial_record_repo.add(older)
    financial_record_repo.add(newer)

    query = FinancialRecordReviewQuery()

    result = financial_record_repo.list_for_review(
        organization_id=org_id,
        query=query,
    )

    assert result[0] == newer
    assert result[1] == older
