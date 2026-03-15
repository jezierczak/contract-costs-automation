from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CounterpartyYearRaw:
    year: int
    invoice_count: int
    revenue: Decimal
    costs: Decimal