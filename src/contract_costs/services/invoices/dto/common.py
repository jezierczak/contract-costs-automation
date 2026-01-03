from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.amount import Amount
from contract_costs.model.invoice import PaymentMethod, PaymentStatus, InvoiceStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.invoices.commands.invoice_command import InvoiceCommand
from contract_costs.services.invoices.dto.export.company_export import CompanyExport


@dataclass(frozen=True)
class InvoiceApplyResult:
    invoice_id: UUID
    invoice_number: str
    command: InvoiceCommand



@dataclass(frozen=True)
class InvoiceUpdate:
    command: InvoiceCommand              # APPLY | DELETE | MODIFY

    invoice_number: str           # nowy numer (None → generator)
    old_invoice_number: str | None       # tylko dla MODIFY / DELETE

    invoice_date: date | None
    selling_date: date | None

    buyer_tax_number: str | None
    seller_tax_number: str | None

    payment_method: PaymentMethod
    due_date: date | None
    payment_status: PaymentStatus
    status: InvoiceStatus

@dataclass(frozen=True)
class ResolvedInvoiceUpdate:
    command: InvoiceCommand

    invoice_number: str
    old_invoice_number: str | None

    invoice_date: date | None
    selling_date: date | None

    buyer_id: UUID
    seller_id: UUID

    payment_method: PaymentMethod
    due_date: date | None
    payment_status: PaymentStatus
    status: InvoiceStatus


@dataclass(frozen=True)
class InvoiceLineUpdate:
    invoice_line_id: UUID | None   # None = nowa linia

    invoice_number: str | None
    item_name: str
    description: str | None
    quantity: Decimal
    unit: UnitOfMeasure
    amount: Amount

    contract_id: str | None
    cost_node_id: str | None
    cost_type_id: str | None

@dataclass(frozen=True)
class InvoiceExcelBatch:
    invoices: list[InvoiceUpdate]
    lines: list[InvoiceLineUpdate]

    buyers: list[CompanyExport]
    sellers: list[CompanyExport]


@dataclass(frozen=True)
class InvoiceIngestBatch:
    invoices: list[ResolvedInvoiceUpdate]
    lines: list[InvoiceLineUpdate]
