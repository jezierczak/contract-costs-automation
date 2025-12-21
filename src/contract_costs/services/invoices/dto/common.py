from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from contract_costs.model.amount import Amount
from contract_costs.model.invoice import PaymentMethod, PaymentStatus, InvoiceStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure


@dataclass(frozen=True)
class InvoiceRef:
    """
    Referencja faktury w Excelu.
    """
    invoice_id: UUID | None      # jeśli faktura już istnieje
    external_ref: str | None     # jeśli faktura nowa (np. "INV-1")


@dataclass(frozen=True)
class InvoiceUpdate:
    ref: InvoiceRef
    invoice_number: str
    invoice_date: date
    selling_date: date
    buyer_id: UUID | None
    seller_id: UUID | None
    payment_method: PaymentMethod
    due_date: date
    payment_status: PaymentStatus
    status: InvoiceStatus


@dataclass(frozen=True)
class InvoiceLineUpdate:
    invoice_line_id: UUID | None   # None = nowa linia
    invoice_ref: InvoiceRef | None # None = koszt bez faktury

    item_name: str
    description: str | None
    quantity: Decimal
    unit: UnitOfMeasure
    amount: Amount

    contract_id: UUID | None
    cost_node_id: UUID | None
    cost_type_id: UUID | None

@dataclass(frozen=True)
class InvoiceExcelBatch:
    invoices: list[InvoiceUpdate]
    lines: list[InvoiceLineUpdate]


