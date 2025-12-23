from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from contract_costs.model.invoice import InvoiceStatus, PaymentMethod, PaymentStatus

@dataclass(frozen=True)
class InvoiceExport:
    invoice_number: str
    invoice_date: date
    selling_date: date

    buyer_tax_number: str
    seller_tax_number: str

    payment_method: PaymentMethod
    payment_status: PaymentStatus
    status: InvoiceStatus

    due_date: date
    timestamp: datetime
