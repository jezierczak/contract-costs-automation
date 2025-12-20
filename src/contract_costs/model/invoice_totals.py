from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class InvoiceTotals:
    invoice_id: UUID
    net: Decimal
    tax: Decimal
    gross: Decimal
