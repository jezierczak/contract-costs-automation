from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class CompanyMonthBreakdownRaw:

    value_type_id: UUID | None
    code: str | None
    name: str | None

    revenue: Decimal
    costs: Decimal
    non_deductible: Decimal