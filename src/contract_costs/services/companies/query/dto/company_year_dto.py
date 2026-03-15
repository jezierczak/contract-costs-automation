from dataclasses import dataclass
from decimal import Decimal


@dataclass
class CounterpartyYearDTO:
    year: int
    invoice_count: int
    revenue: Decimal
    costs: Decimal
    balance: Decimal