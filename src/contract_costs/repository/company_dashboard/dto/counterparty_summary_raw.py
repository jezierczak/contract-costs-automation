from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True)
class CounterpartySummaryRaw:
    invoice_count: int

    revenue: Decimal
    costs: Decimal

    unpaid_invoices: int
    last_invoice_date: date | None