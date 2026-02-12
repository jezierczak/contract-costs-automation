from datetime import date

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.financial_record import PaymentStatus, FinancialRecordStatus
from tests.builders.financial_record_builder import FinancialRecordBuilder


def test_mark_paid_returns_new_instance():
    record = FinancialRecordBuilder().build()

    updated = record.mark_paid(
        updated_at=utc_now(),
        updated_by_user_id=new_uuid(),
        paid_at=date(2024, 1, 1),
    )

    assert updated.payment_status == PaymentStatus.PAID
    assert updated.paid_date == date(2024, 1, 1)

    # oryginał bez zmian
    assert record.payment_status == PaymentStatus.UNPAID
    assert record.paid_date is None
    assert updated is not record

def test_mark_unpaid_resets_paid_date():
    record = FinancialRecordBuilder().build()

    paid = record.mark_paid(
        updated_at=utc_now(),
        updated_by_user_id=new_uuid(),
        paid_at=date(2024, 1, 1),
    )

    unpaid = paid.mark_unpaid(
        updated_at=utc_now(),
        updated_by_user_id=new_uuid(),
    )

    assert unpaid.payment_status == PaymentStatus.UNPAID
    assert unpaid.paid_date is None


def test_mark_sent_to_accountant_changes_status():
    record = FinancialRecordBuilder().build()

    updated = record.mark_sent_to_accountant(
        updated_at=utc_now(),
        updated_by_user_id=new_uuid(),
    )

    assert updated.status == FinancialRecordStatus.SENT_TO_ACCOUNTANT

def test_reopen_sets_status_to_in_progress():
    record = FinancialRecordBuilder().build()

    updated = record.reopen(
        updated_at=utc_now(),
        updated_by_user_id=new_uuid(),
    )

    assert updated.status == FinancialRecordStatus.IN_PROGRESS


def test_mark_paid_sets_audit_fields():
    user_id = new_uuid()
    now = utc_now()

    record = FinancialRecordBuilder().build()

    updated = record.mark_paid(
        updated_at=now,
        updated_by_user_id=user_id,
        paid_at=None,
    )

    assert updated.updated_at == now
    assert updated.updated_by_user_id == user_id

import pytest

def test_financial_record_disallows_dynamic_attributes():
    record = FinancialRecordBuilder().build()

    with pytest.raises(AttributeError):
        record.some_random_field = 123
