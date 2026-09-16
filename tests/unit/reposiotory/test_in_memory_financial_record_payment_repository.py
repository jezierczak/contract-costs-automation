from decimal import Decimal

from contract_costs.common.ids import new_uuid
from tests.builders.financial_record_payment_builder import FinancialRecordPaymentBuilder


def test_add_and_list_by_financial_record(financial_record_payment_repo):
    org_id = new_uuid()
    record_id = new_uuid()

    payment = (
        FinancialRecordPaymentBuilder()
        .with_organization_id(org_id)
        .with_financial_record_id(record_id)
        .with_amount(Decimal("250.00"))
        .build()
    )

    financial_record_payment_repo.add(organization_id=org_id, payment=payment)

    result = financial_record_payment_repo.list_by_financial_record(
        organization_id=org_id, financial_record_id=record_id,
    )

    assert result == [payment]


def test_list_isolated_by_org(financial_record_payment_repo):
    org1 = new_uuid()
    org2 = new_uuid()
    record_id = new_uuid()

    payment = (
        FinancialRecordPaymentBuilder()
        .with_organization_id(org1)
        .with_financial_record_id(record_id)
        .build()
    )
    financial_record_payment_repo.add(organization_id=org1, payment=payment)

    assert financial_record_payment_repo.list_by_financial_record(
        organization_id=org2, financial_record_id=record_id,
    ) == []


def test_get_returns_none_for_wrong_org(financial_record_payment_repo):
    org1 = new_uuid()
    org2 = new_uuid()

    payment = FinancialRecordPaymentBuilder().with_organization_id(org1).build()
    financial_record_payment_repo.add(organization_id=org1, payment=payment)

    assert financial_record_payment_repo.get(organization_id=org2, payment_id=payment.id) is None
    assert financial_record_payment_repo.get(organization_id=org1, payment_id=payment.id) == payment


def test_delete_removes_payment(financial_record_payment_repo):
    org_id = new_uuid()
    payment = FinancialRecordPaymentBuilder().with_organization_id(org_id).build()
    financial_record_payment_repo.add(organization_id=org_id, payment=payment)

    financial_record_payment_repo.delete(organization_id=org_id, payment_id=payment.id)

    assert financial_record_payment_repo.get(organization_id=org_id, payment_id=payment.id) is None


def test_delete_all_by_financial_record(financial_record_payment_repo):
    org_id = new_uuid()
    record_id = new_uuid()

    for amount in (Decimal("100.00"), Decimal("200.00")):
        payment = (
            FinancialRecordPaymentBuilder()
            .with_organization_id(org_id)
            .with_financial_record_id(record_id)
            .with_amount(amount)
            .build()
        )
        financial_record_payment_repo.add(organization_id=org_id, payment=payment)

    deleted = financial_record_payment_repo.delete_all_by_financial_record(
        organization_id=org_id, financial_record_id=record_id,
    )

    assert deleted == 2
    assert financial_record_payment_repo.list_by_financial_record(
        organization_id=org_id, financial_record_id=record_id,
    ) == []
