from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID
from datetime import date


@dataclass
class CompanyFixedCostRaw:

    record_id: UUID
    record_date: date

    contract_id: UUID
    contract_code: str | None

    value_type_code: str | None
    value_type_name: str | None

    description: str | None

    amount: Decimal
    tax_treatment: str