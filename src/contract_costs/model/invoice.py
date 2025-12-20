from  dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from uuid import UUID
from datetime import date, datetime

from contract_costs.model.company import Company
from contract_costs.model.invoice_line import InvoiceLine

class PaymentMethod(Enum):
    BANK_TRANSFER = "bank_transfer"   # przelew
    CASH = "cash"                     # gotówka
    CARD = "card"                     # karta
    BLIK = "blik"                     # BLIK

class PaymentStatus(Enum):
    UNPAID = "unpaid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"

class InvoiceStatus(Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    PROCESSED = "processed"


@dataclass
class Invoice:
    id: UUID

    invoice_number: str
    invoice_date: date
    selling_date: date


    buyer_id: UUID
    seller_id: UUID

    # lines: list[InvoiceLine]

    payment_method: PaymentMethod
    due_date: date
    payment_status: PaymentStatus

    status: InvoiceStatus

    timestamp: datetime



    # @property
    # def net_total(self) -> Decimal:
    #     return sum(
    #         (line.amount.net or Decimal("0.00") for line in self.lines),
    #         start=Decimal("0.00")
    #     )
    # @property
    # def tax_total(self) -> Decimal:
    #     return sum(
    #         (line.amount.tax for line in self.lines),
    #         start=Decimal("0.00")
    #     )
    # @property
    # def gross_total(self) -> Decimal:
    #     return sum(
    #         (line.amount.gross for line in self.lines),
    #         start=Decimal("0.00")
    #     )

