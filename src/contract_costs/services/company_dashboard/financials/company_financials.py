from dataclasses import dataclass, field
from decimal import Decimal

from contract_costs.services.common.pillars import Pillars


@dataclass(frozen=True)
class CompanyPeriodFinancials:
    """Finanse firmy w okresie (miesiąc, rok, typ wartości) — trzy filary z Amount."""

    revenue: Pillars = Pillars()
    cost: Pillars = Pillars()    # wszystkie koszty, łącznie ze stałymi
    fixed: Pillars = Pillars()   # w tym koszty stałe — utrzymanie firmy (ZUS, podatki, księgowość, bank)

    @property
    def result_net(self) -> Decimal:
        return self.revenue.net - self.cost.net

    @property
    def result_cashflow(self) -> Decimal:
        return self.revenue.cashflow - self.cost.cashflow

    def __add__(self, other: "CompanyPeriodFinancials") -> "CompanyPeriodFinancials":
        return CompanyPeriodFinancials(
            revenue=self.revenue + other.revenue,
            cost=self.cost + other.cost,
            fixed=self.fixed + other.fixed,
        )


@dataclass(frozen=True)
class CompanyValueTypeFinancials:
    value_type_id: str | None
    code: str | None
    name: str | None
    is_fixed: bool
    financials: CompanyPeriodFinancials


@dataclass(frozen=True)
class CompanyFinancials:
    year: int
    total: CompanyPeriodFinancials
    # tylko miesiące, w których były linie; klucz = numer miesiąca
    months: dict[int, CompanyPeriodFinancials] = field(default_factory=dict)
    # rekordy jeszcze niezatwierdzone (w trakcie przypisywania) — nie wchodzą do sum
    unapproved_record_count: int = 0
