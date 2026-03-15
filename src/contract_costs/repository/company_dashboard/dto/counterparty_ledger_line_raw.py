from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID


@dataclass(slots=True)
class CounterpartyLedgerLineRaw:
    record_id: UUID
    record_date: date

    buyer_id: UUID | None
    seller_id: UUID | None

    amount_value: Decimal
    amount_input_type: str
    vat_rate: str
    tax_treatment: str

    payment_status: str