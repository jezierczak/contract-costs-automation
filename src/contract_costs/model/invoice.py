from  dataclasses import dataclass

from enum import Enum
from uuid import UUID
from datetime import date, datetime


class PaymentMethod(Enum):
    PRE_PAID = "pre_paid"
    BANK_TRANSFER = "bank_transfer"   # przelew
    CASH = "cash"                     # gotówka
    CARD = "card"                     # karta
    BLIK = "blik"                     # BLIK
    UNKNOWN = "unknown"

class PaymentStatus(Enum):
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    UNKNOWN = "unknown"

class InvoiceStatus(Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PROCESSED = "processed"
    DELETED = "deleted"
    MODIFIED = "modified"
    # REFERENCE = "reference"


@dataclass
class Invoice:
    id: UUID

    invoice_number: str
    invoice_date: date | None
    selling_date: date | None


    buyer_id: UUID
    seller_id: UUID

    payment_method: PaymentMethod
    due_date: date | None
    payment_status: PaymentStatus

    status: InvoiceStatus

    timestamp: datetime



