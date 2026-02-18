from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.amount import Amount
from contract_costs.model.company import Company
from contract_costs.model.financial_record import PaymentMethod, PaymentStatus, FinancialRecordStatus, FinancialRecord
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import InvoiceCommand
from contract_costs.services.financial_records.assigment.prepare.dto.company_export import CompanyExport


# @dataclass(frozen=True)
# class InvoiceApplyResult:
#     invoice_id: UUID
#     invoice_number: str
#     command: InvoiceCommand



@dataclass(frozen=True)
class FinancialRecordUpdate:
    command: InvoiceCommand              # APPLY | DELETE | MODIFY

    reference: str           # nowy numer (None → generator)
    record_id: UUID | None
    old_reference: str | None       # tylko dla MODIFY / DELETE

    invoice_date: date | None
    selling_date: date | None

    buyer_tax_number: str | None
    seller_tax_number: str | None

    payment_method: PaymentMethod
    due_date: date | None
    paid_date: date | None
    # scan_filename: str | None
    tags: str | None
    payment_status: PaymentStatus
    status: FinancialRecordStatus

@dataclass(frozen=True)
class ResolvedFinancialRecordUpdate:
    command: InvoiceCommand

    reference: str
    record_id: UUID | None
    old_record_reference: str | None

    invoice_date: date | None
    selling_date: date | None

    buyer: Company
    seller: Company

    payment_method: PaymentMethod
    due_date: date | None
    payment_status: PaymentStatus
    status: FinancialRecordStatus

    paid_date: date | None
    # scan_filename: str | None
    tags: str| None


@dataclass(frozen=True)
class FinancialRecordLineUpdate:
    record_line_id: UUID | None   # None = nowa linia

    record_reference: str | None
    item_name: str
    description: str | None
    quantity: Decimal
    unit: UnitOfMeasure
    amount: Amount

    contract_code: str | None
    contract_node_code: str | None
    value_type_code: str | None
    agreement_code: str | None
    agreement_node_code: str | None


@dataclass(frozen=True)
class InvoiceExcelBatch:
    financial_records: list[FinancialRecordUpdate]
    lines: list[FinancialRecordLineUpdate]

    buyers: list[CompanyExport]
    sellers: list[CompanyExport]


@dataclass(frozen=True)
class RecordIngestBatch:
    financial_records: list[ResolvedFinancialRecordUpdate]
    lines: list[FinancialRecordLineUpdate]
