from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from contract_costs.model.invoice import InvoiceStatus, PaymentMethod, PaymentStatus
from contract_costs.services.invoices.commands.invoice_command import InvoiceCommand


@dataclass(frozen=True)
class InvoiceExport:
    action: InvoiceCommand | None
    invoice_number: str
    invoice_date: date | None
    selling_date: date | None

    buyer_tax_number: str | None
    seller_tax_number: str | None

    payment_method: PaymentMethod
    payment_status: PaymentStatus
    status: InvoiceStatus

    due_date: date | None
    timestamp: datetime
