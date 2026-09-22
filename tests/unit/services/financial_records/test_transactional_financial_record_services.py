from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from contract_costs.model.amount import Amount, AmountInputType, TaxTreatment, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.financial_record import PaymentStatus
from contract_costs.services.financial_records.actions.dto.invoice_action_command import (
    FinancialRecordAction,
    FinancialRecordActionCommand,
    FinancialRecordSelector,
)
from contract_costs.services.financial_records.actions.financial_record_action_service import FinancialRecordActionService
from contract_costs.services.financial_records.assigment.apply.apply_financial_record_excel_batch_service import (
    ApplyFinancialRecordExcelBatchService,
)
from contract_costs.services.financial_records.assigment.apply.commands.apply_invoice_excel_bach_command import (
    ApplyInvoiceExcelBatchCommand,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import InvoiceExcelBatch
from contract_costs.services.financial_records.assigment.prepare.dto.company_export import CompanyExport
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder


class _FakeCompanyApplyService:
    def __init__(self):
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)


class _FakeExcelResolver:
    def __init__(self):
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)
        return kwargs["action"].batch


class _FakeIngestOrchestrator:
    def __init__(self):
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)


def test_financial_record_action_service_uses_uow():
    uow = InMemoryUnitOfWork()
    org_id = uuid4()
    actor_id = uuid4()

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_payment_status(PaymentStatus.PAID)
        .build()
    )
    uow.financial_records.add(record)

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(org_id)
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
    uow.financial_record_lines.add(organization_id=org_id, line=line)

    service = FinancialRecordActionService(clock=lambda: datetime(2026, 2, 16, 12, 0, 0))
    action = FinancialRecordActionCommand(
        organization_id=org_id,
        actor_user_id=actor_id,
        action=FinancialRecordAction.MARK_UNPAID,
        selectors=[FinancialRecordSelector(record_id=record.id)],
        payload=None,
    )

    service.execute(action=action, uow=uow)

    updated = uow.financial_records.get(organization_id=org_id, record_id=record.id)
    assert updated is not None
    assert updated.payment_status == PaymentStatus.UNPAID


def test_apply_financial_record_batch_passes_uow_to_dependencies():
    uow = InMemoryUnitOfWork()

    company_apply = _FakeCompanyApplyService()
    excel_resolver = _FakeExcelResolver()
    ingest = _FakeIngestOrchestrator()

    service = ApplyFinancialRecordExcelBatchService(
        excel_resolver=excel_resolver,
        company_apply_service=company_apply,
        orchestrator=ingest,
    )

    cmd = ApplyInvoiceExcelBatchCommand(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        batch=InvoiceExcelBatch(
            financial_records=[],
            lines=[],
            buyers=[CompanyExport(id=uuid4(), name="B", tax_number="123")],
            sellers=[CompanyExport(id=uuid4(), name="S", tax_number="456")],
        ),
    )

    service.execute(action=cmd, uow=uow)

    assert len(company_apply.calls) == 2
    assert company_apply.calls[0]["uow"] is uow
    assert company_apply.calls[1]["uow"] is uow
    assert excel_resolver.calls[0]["uow"] is uow
    assert ingest.calls[0]["uow"] is uow
