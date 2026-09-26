from dataclasses import dataclass
from decimal import Decimal

from contract_costs.model.amount import Amount

ZERO = Decimal("0")


@dataclass(frozen=True)
class Pillars:
    """Trzy filary kwot liczone wyłącznie z Amount (wspólne dla kontraktów i firm)."""

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
