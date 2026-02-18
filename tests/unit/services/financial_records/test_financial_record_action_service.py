from datetime import date, datetime
from uuid import uuid4

import pytest

from contract_costs.model.financial_record import (
    FinancialRecordStatus,
    PaymentStatus,
)
from contract_costs.services.financial_records.actions.dto.invoice_action_command import (
    FinancialRecordAction,
    FinancialRecordActionCommand,
    FinancialRecordSelector,
)
from contract_costs.services.financial_records.actions.financial_record_action_service import (
    FinancialRecordActionService,
)
from tests.builders.financial_record_builder import FinancialRecordBuilder


def test_mark_paid_updates_payment_status_and_paid_date(financial_record_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    paid_at = date(2026, 2, 12)
    now = datetime(2026, 2, 12, 22, 0, 0)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_payment_status(PaymentStatus.UNPAID)
        .build()
    )
    financial_record_repo.add(record)

    service = FinancialRecordActionService(
        clock=lambda: now,
    )
    cmd = FinancialRecordActionCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=FinancialRecordAction.MARK_PAID,
        selectors=[FinancialRecordSelector(record_id=record.id)],
        payload={"paid_at": paid_at},
    )

    service.execute(action=cmd, uow=uow)

    updated = financial_record_repo.get(organization_id=organization_id, record_id=record.id)
    assert updated is not None
    assert updated.payment_status == PaymentStatus.PAID
    assert updated.paid_date == paid_at
    assert updated.updated_at == now
    assert updated.updated_by_user_id == actor_user_id


def test_mark_sent_to_accountant_skips_non_processed(financial_record_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_status(FinancialRecordStatus.DRAFT)
        .build()
    )
    financial_record_repo.add(record)

    service = FinancialRecordActionService()
    cmd = FinancialRecordActionCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=FinancialRecordAction.MARK_SENT_TO_ACCOUNTANT,
        selectors=[FinancialRecordSelector(record_id=record.id)],
        payload=None,
    )

    service.execute(action=cmd, uow=uow)

    unchanged = financial_record_repo.get(organization_id=organization_id, record_id=record.id)
    assert unchanged is not None
    assert unchanged.status == FinancialRecordStatus.DRAFT


def test_reopen_raises_for_not_closed_record(financial_record_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_status(FinancialRecordStatus.DRAFT)
        .build()
    )
    financial_record_repo.add(record)

    service = FinancialRecordActionService()
    cmd = FinancialRecordActionCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=FinancialRecordAction.REOPEN,
        selectors=[FinancialRecordSelector(record_id=record.id)],
        payload=None,
    )

    with pytest.raises(ValueError, match="not closed or processed"):
        service.execute(action=cmd, uow=uow)
