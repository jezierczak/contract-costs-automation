from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum
from uuid import UUID

from contract_costs.model.amount import Amount

ZERO = Decimal("0")

# poniżej tego postępu prognoza na koniec jest zbyt niepewna, żeby ją pokazywać
MIN_PROGRESS_FOR_FORECAST = Decimal("0.05")


@dataclass(frozen=True)
class Pillars:
    """Trzy filary kwot liczone wyłącznie z Amount."""

    net: Decimal = ZERO        # księgowe — obniża podatek (z amortyzacją)
    non_tax: Decimal = ZERO    # nieksięgowe — wydatek, który nie obniża podatku
    cashflow: Decimal = ZERO   # realny przepływ pieniężny (netto)

    @classmethod
    def of(cls, amount: Amount) -> "Pillars":
        return cls(
            net=amount.net,
            non_tax=amount.non_tax_cost,
            cashflow=amount.cashflow,
        )

    def __add__(self, other: "Pillars") -> "Pillars":
        return Pillars(
            net=self.net + other.net,
            non_tax=self.non_tax + other.non_tax,
            cashflow=self.cashflow + other.cashflow,
        )


@dataclass(frozen=True)
class ScopeFinancials:
    """Finanse zakresu kontraktu — węzła albo całego kontraktu."""

    budget: Decimal            # wartość sprzedażowa
    progress: Decimal | None   # 0..1, None gdy nikt nie wpisał postępu
    cost: Pillars
    revenue: Pillars

    @property
    def executed(self) -> Decimal | None:
        if self.progress is None:
            return None
        return self.budget * self.progress

    @property
    def result_net(self) -> Decimal:
        return self.revenue.net - self.cost.net

    @property
    def result_cashflow(self) -> Decimal:
        return self.revenue.cashflow - self.cost.cashflow

    @property
    def result_on_progress(self) -> Decimal | None:
        # predyktor na żywo — niezależny od terminów płatności klienta
        if self.executed is None:
            return None
        return self.executed - self.cost.cashflow

    @property
    def forecast_total_cost(self) -> Decimal | None:
        if self.progress is None or self.progress < MIN_PROGRESS_FOR_FORECAST:
            return None
        return self.cost.cashflow / self.progress

    @property
    def forecast_result(self) -> Decimal | None:
        if self.forecast_total_cost is None:
            return None
        return self.budget - self.forecast_total_cost

    @property
    def billing_gap(self) -> Decimal | None:
        # < 0 — niedofakturowane (praca wykonana, faktury jeszcze nie ma)
        if self.executed is None:
            return None
        return self.revenue.net - self.executed


class IndicatorLevel(Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


@dataclass(frozen=True)
class ContractIndicators:
    cost: IndicatorLevel | None
    schedule: IndicatorLevel | None
    billing: IndicatorLevel | None
    time_progress: Decimal | None
    last_progress_date: date | None
    progress_stale: bool | None


@dataclass(frozen=True)
class ContractFinancials:
    total: ScopeFinancials
    nodes: dict[UUID, ScopeFinancials]
    indicators: ContractIndicators
