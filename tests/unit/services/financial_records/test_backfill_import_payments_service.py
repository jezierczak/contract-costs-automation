from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from contract_costs.common.ids import new_uuid
from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.financial_record import (
    FinancialRecordStatus,
    PaymentMethod,
    PaymentStatus,
)
from contract_costs.model.financial_record_payment import FinancialRecordPayment
from contract_costs.services.financial_records.actions.financial_record_action_service import (
    FinancialRecordActionService,
)
from contract_costs.services.financial_records.migration.backfill_import_payments_command import (
    BackfillImportPaymentsCommand,
)
from contract_costs.services.financial_records.migration.backfill_import_payments_service import (
    BackfillImportPaymentsService,
)
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder

ORG = uuid4()
NOW = datetime(2026, 9, 26, 12, 0)


def _add_record(uow, *, method, status, net="1000.00", paid_date=None, record_status=None):
    builder = (
        FinancialRecordBuilder()
        .with_organization_id(ORG)
        .with_invoice_date(date(2026, 9, 15))
        .with_payment_method(method)
        .with_payment_status(status)
        .with_paid_date(paid_date)
    )
    if record_status is not None:
        builder = builder.with_status(record_status)
    record = builder.build()
    uow.financial_records.add(record)
    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(ORG)
        .with_financial_record_id(record.id)
        .with_amount(
            Amount(
                value=Decimal(net),
                input_type=AmountInputType.NET,
                vat_rate=VatRate.VAT_23,
                tax_treatment=TaxTreatment.TAX_DEDUCTIBLE,
            )
        )
        .build()
    )
    uow.financial_record_lines.add(organization_id=ORG, line=line)
    return record


def _add_payment(uow, record, amount):
    uow.financial_record_payments.add(
        organization_id=ORG,
        payment=FinancialRecordPayment(
            id=new_uuid(),
            organization_id=ORG,
            created_at=NOW,
            created_by_user_id=uuid4(),
            updated_at=None,
            updated_by_user_id=None,
            financial_record_id=record.id,
            amount=Decimal(amount),
            paid_date=date(2026, 9, 20),
        ),
    )


def _run(uow, apply):
    service = BackfillImportPaymentsService(
        action_service=FinancialRecordActionService(clock=lambda: NOW),
    )
    return service.execute(
        action=BackfillImportPaymentsCommand(organization_id=ORG, actor_user_id=uuid4(), apply=apply),
        uow=uow,
    )


def _payments(uow, record):
    return uow.financial_record_payments.list_by_financial_record(
        organization_id=ORG, financial_record_id=record.id,
    )


def _seed(uow):
    return {
        "cash_unpaid": _add_record(uow, method=PaymentMethod.CASH, status=PaymentStatus.UNPAID),
        "blik_unknown": _add_record(uow, method=PaymentMethod.BLIK, status=PaymentStatus.UNKNOWN),
        "transfer_paid_no_payment": _add_record(
            uow, method=PaymentMethod.BANK_TRANSFER, status=PaymentStatus.PAID, paid_date=date(2026, 9, 18),
        ),
        "transfer_unpaid": _add_record(uow, method=PaymentMethod.BANK_TRANSFER, status=PaymentStatus.UNPAID),
        "card_deleted": _add_record(
            uow, method=PaymentMethod.CARD, status=PaymentStatus.UNPAID,
            record_status=FinancialRecordStatus.DELETED,
        ),
    }


def test_dry_run_lists_fixes_without_writing(uow):
    records = _seed(uow)
    paid_ok = _add_record(uow, method=PaymentMethod.CARD, status=PaymentStatus.PAID)
    _add_payment(uow, paid_ok, "1230.00")

    fixes = _run(uow, apply=False)

    assert {f.record_id for f in fixes} == {
        records["cash_unpaid"].id,
        records["blik_unknown"].id,
        records["transfer_paid_no_payment"].id,
    }
    by_id = {f.record_id: f for f in fixes}
    assert by_id[records["cash_unpaid"].id].missing == Decimal("1230.00")
    assert by_id[records["cash_unpaid"].id].paid_date == date(2026, 9, 15)
    assert by_id[records["transfer_paid_no_payment"].id].paid_date == date(2026, 9, 18)
    assert all(_payments(uow, r) == [] for r in records.values())
    assert uow.financial_records.get(
        organization_id=ORG, record_id=records["cash_unpaid"].id,
    ).payment_status == PaymentStatus.UNPAID


def test_apply_adds_missing_payments_and_marks_paid(uow):
    records = _seed(uow)

    _run(uow, apply=True)

    for key in ("cash_unpaid", "blik_unknown", "transfer_paid_no_payment"):
        record = uow.financial_records.get(organization_id=ORG, record_id=records[key].id)
        [payment] = _payments(uow, record)
        assert payment.amount == Decimal("1230.00")
        assert record.payment_status == PaymentStatus.PAID
    assert _payments(uow, records["transfer_unpaid"]) == []
    assert _payments(uow, records["card_deleted"]) == []
    assert _run(uow, apply=False) == []


def test_partially_paid_cash_gets_only_the_remainder(uow):
    record = _add_record(uow, method=PaymentMethod.CASH, status=PaymentStatus.PARTIALLY_PAID)
    _add_payment(uow, record, "230.00")

    [fix] = _run(uow, apply=True)

    assert fix.missing == Decimal("1000.00")
    assert sorted(p.amount for p in _payments(uow, record)) == [Decimal("230.00"), Decimal("1000.00")]
