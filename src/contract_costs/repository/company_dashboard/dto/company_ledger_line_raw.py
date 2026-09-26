from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(slots=True)
class CompanyLedgerLineRaw:
    """Pojedyncza linia z financial_ledger — bez żadnych sum, kwoty liczy Amount."""

    record_id: str
    record_date: date

    buyer_id: str
    seller_id: str

    direction: str | None
    contract_type: str | None
    contract_owner_id: str | None

    value_type_id: str | None
    value_type_code: str | None
    value_type_name: str | None

    item_name: str | None
    description: str | None

    amount_value: Decimal
    amount_input_type: str
    vat_rate: Decimal
    tax_treatment: str

    status: str
