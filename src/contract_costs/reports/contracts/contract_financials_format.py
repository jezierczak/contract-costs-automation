from decimal import Decimal

from contract_costs.services.contracts.financials.contract_financials import IndicatorLevel

_CENTS = Decimal("0.01")


def money(value: Decimal | None) -> Decimal | None:
    return value.quantize(_CENTS) if value is not None else None


def percent(value: Decimal | None) -> str:
    return f"{value * 100:.1f}%" if value is not None else "-"


def level(value: IndicatorLevel | None) -> str:
    return value.value if value is not None else "-"
