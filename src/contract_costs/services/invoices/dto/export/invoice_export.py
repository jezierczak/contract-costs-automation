from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from contract_costs.model.invoice import InvoiceStatus, PaymentMethod, PaymentStatus

@dataclass(frozen=True)
class InvoiceExport:
    id: UUID
    invoice_number: str
    invoice_date: date
    selling_date: date

    buyer_id: UUID
    seller_id: UUID

    payment_method: PaymentMethod
    payment_status: PaymentStatus
    status: InvoiceStatus

    due_date: date
    timestamp: datetime
