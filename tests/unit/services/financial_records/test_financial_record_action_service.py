from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
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
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder


def test_mark_paid_updates_payment_status_and_paid_date(financial_record_repo, line_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    paid_date = date(2026, 2, 12)
    now = datetime(2026, 2, 12, 22, 0, 0)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_payment_status(PaymentStatus.UNPAID)
        .build()
    )
    financial_record_repo.add(record)

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(organization_id)
        .with_financial_record_id(record.id)
        .with_amount(
            Amount(
                value=Decimal("1000.00"),
                input_type=AmountInputType.NET,
                vat_rate=VatRate.VAT_23,
                tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
            )
        )
        .build()
    )
    line_repo.add(organization_id=organization_id, line=line)

    service = FinancialRecordActionService(
        clock=lambda: now,
    )
    cmd = FinancialRecordActionCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=FinancialRecordAction.MARK_PAID,
        selectors=[FinancialRecordSelector(record_id=record.id)],
        payload={"paid_date": paid_date},
    )

    service.execute(action=cmd, uow=uow)

    updated = financial_record_repo.get(organization_id=organization_id, record_id=record.id)
    assert updated is not None
    assert updated.payment_status == PaymentStatus.PAID
    assert updated.paid_date == paid_date
    assert updated.updated_at == now
    assert updated.updated_by_user_id == actor_user_id

    payments = uow.financial_record_payments.list_by_financial_record(
        organization_id=organization_id, financial_record_id=record.id,
    )
    assert len(payments) == 1
    assert payments[0].amount == Decimal("1000.00")


def test_mark_paid_auto_pays_when_no_cashflow(financial_record_repo, uow):
    """
    Rekord bez linii (lub z samych linii non_cash_cost) ma total_cashflow == 0 –
    nie ma czego płacić, więc z automatu dostaje status PAID zamiast wisieć jako UNPAID.
    """
    organization_id = uuid4()
    actor_user_id = uuid4()

    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_payment_status(PaymentStatus.UNPAID)
        .build()
    )
    financial_record_repo.add(record)

    service = FinancialRecordActionService()
    cmd = FinancialRecordActionCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        action=FinancialRecordAction.MARK_PAID,
        selectors=[FinancialRecordSelector(record_id=record.id)],
        payload={"paid_date": date(2026, 2, 12)},
    )

    service.execute(action=cmd, uow=uow)

    updated = financial_record_repo.get(organization_id=organization_id, record_id=record.id)
    assert updated.payment_status == PaymentStatus.PAID
    assert updated.paid_date is None


def test_add_payment_then_mark_paid_tops_up_remaining(financial_record_repo, line_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()

    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_payment_status(PaymentStatus.UNPAID)
        .build()
    )
    financial_record_repo.add(record)

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(organization_id)
        .with_financial_record_id(record.id)
        .with_amount(
            Amount(
                value=Decimal("1000.00"),
                input_type=AmountInputType.NET,
                vat_rate=VatRate.VAT_23,
                tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
            )
        )
        .build()
    )
    line_repo.add(organization_id=organization_id, line=line)

    service = FinancialRecordActionService()

    service.execute(
        action=FinancialRecordActionCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=FinancialRecordAction.ADD_PAYMENT,
            selectors=[FinancialRecordSelector(record_id=record.id)],
            payload={"amount": Decimal("400.00"), "paid_date": date(2026, 3, 5)},
        ),
        uow=uow,
    )

    partially_paid = financial_record_repo.get(organization_id=organization_id, record_id=record.id)
    assert partially_paid.payment_status == PaymentStatus.PARTIALLY_PAID

    service.execute(
        action=FinancialRecordActionCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=FinancialRecordAction.MARK_PAID,
            selectors=[FinancialRecordSelector(record_id=record.id)],
            payload={"paid_date": date(2026, 3, 10)},
        ),
        uow=uow,
    )

    fully_paid = financial_record_repo.get(organization_id=organization_id, record_id=record.id)
    assert fully_paid.payment_status == PaymentStatus.PAID
    assert fully_paid.paid_date == date(2026, 3, 10)

    payments = uow.financial_record_payments.list_by_financial_record(
        organization_id=organization_id, financial_record_id=record.id,
    )
    assert len(payments) == 2
    assert sum(p.amount for p in payments) == Decimal("1000.00")


def test_mark_unpaid_wipes_payment_history(financial_record_repo, line_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()

    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_payment_status(PaymentStatus.UNPAID)
        .build()
    )
    financial_record_repo.add(record)

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(organization_id)
        .with_financial_record_id(record.id)
        .with_amount(
            Amount(
                value=Decimal("1000.00"),
                input_type=AmountInputType.NET,
                vat_rate=VatRate.VAT_23,
                tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
            )
        )
        .build()
    )
    line_repo.add(organization_id=organization_id, line=line)

    service = FinancialRecordActionService()

    service.execute(
        action=FinancialRecordActionCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=FinancialRecordAction.MARK_PAID,
            selectors=[FinancialRecordSelector(record_id=record.id)],
            payload={"paid_date": date(2026, 3, 10)},
        ),
        uow=uow,
    )

    service.execute(
        action=FinancialRecordActionCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            action=FinancialRecordAction.MARK_UNPAID,
            selectors=[FinancialRecordSelector(record_id=record.id)],
            payload=None,
        ),
        uow=uow,
    )

    reset = financial_record_repo.get(organization_id=organization_id, record_id=record.id)
    assert reset.payment_status == PaymentStatus.UNPAID
    assert reset.paid_date is None

    payments = uow.financial_record_payments.list_by_financial_record(
        organization_id=organization_id, financial_record_id=record.id,
    )
    assert payments == []


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
