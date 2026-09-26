from dataclasses import dataclass
from decimal import Decimal

from contract_costs.services.common.pillars import Pillars


@dataclass(slots=True)
class CompanyMonthBreakdownItem:

    code: str | None
    name: str | None
    is_fixed: bool

    pillars: Pillars

    # udział w cashflow kierunku (koszty albo przychody), 0..1
    share: Decimal | None
