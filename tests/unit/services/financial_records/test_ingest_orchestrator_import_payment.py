from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.financial_record import PaymentStatus
from contract_costs.services.financial_records.assigment.ingest.dto.financial_record_ingest_command import (
    IngestFinancialRecordFromDocumentCommand,
)
from contract_costs.services.financial_records.assigment.ingest.financial_record_ingest_orchestrator import (
    FinancialRecordIngestOrchestrator,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import RecordIngestBatch
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder

NOW = datetime(2026, 9, 26, 12, 0)


class StubDocumentIngest:
    """Udaje zapis rekordu z dokumentu – rekord jest już przygotowany w teście."""

    def __init__(self, record):
        self._record = record

    def apply(self, *, uow, organization_id, actor_user_id, updates):
        uow.financial_records.add(self._record)
        return {self._record.reference: SimpleNamespace(record_id=self._record.id)}


class StubLineService:
    def __init__(self, lines):
        self._lines = lines

    def apply(self, *, organization_id, actor_user_id, lines, ref_map, uow):
        for line in self._lines:
            uow.financial_record_lines.add(organization_id=organization_id, line=line)


def _ingest(uow, record, line_amounts):
    lines = [
        FinancialRecordLineBuilder()
        .with_organization_id(record.organization_id)
        .with_financial_record_id(record.id)
        .with_amount(amount)
        .build()
        for amount in line_amounts
    ]
    orchestrator = FinancialRecordIngestOrchestrator(
        record_ingest_service_document=StubDocumentIngest(record),
        record_ingest_service_excel=None,
        record_line_service=StubLineService(lines),
        file_workflow=None,
        record_completion_validator=None,
        clock=lambda: NOW,
    )
    orchestrator.execute(
        action=IngestFinancialRecordFromDocumentCommand(
            organization_id=record.organization_id,
            actor_user_id=uuid4(),
            batch=RecordIngestBatch(financial_records=[], lines=[]),
        ),
        uow=uow,
    )
    return uow.financial_record_payments.list_by_financial_record(
        organization_id=record.organization_id, financial_record_id=record.id,
    )


def _record(status, paid_date=None):
    return (
        FinancialRecordBuilder()
        .with_organization_id(uuid4())
        .with_invoice_date(date(2026, 9, 15))
        .with_payment_status(status)
        .with_paid_date(paid_date)
        .build()
    )


def _net(value, tax_treatment=TaxTreatment.TAX_DEDUCTIBLE):
    return Amount(
        value=Decimal(value),
        input_type=AmountInputType.NET,
        vat_rate=VatRate.VAT_23,
        tax_treatment=tax_treatment,
    )


def test_paid_document_gets_payment_for_full_payable(uow):
    record = _record(PaymentStatus.PAID)

    payments = _ingest(uow, record, [_net("1000.00"), _net("100.00")])

    assert len(payments) == 1
    assert payments[0].amount == Decimal("1353.00")  # 1100 netto + 23% VAT
    assert payments[0].paid_date == date(2026, 9, 15)
    assert payments[0].created_at == NOW


def test_payment_uses_paid_date_from_document(uow):
    record = _record(PaymentStatus.PAID, paid_date=date(2026, 9, 17))

    [payment] = _ingest(uow, record, [_net("10.00")])

    assert payment.paid_date == date(2026, 9, 17)


def test_unpaid_document_gets_no_payment(uow):
    payments = _ingest(uow, _record(PaymentStatus.UNPAID), [_net("1000.00")])

    assert payments == []


def test_paid_document_with_nothing_payable_gets_no_payment(uow):
    record = _record(PaymentStatus.PAID)

    payments = _ingest(uow, record, [_net("50.00", TaxTreatment.NON_CASH_COST)])

    assert payments == []
