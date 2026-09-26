from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

from contract_costs.common.time import APP_TIMEZONE

_CENTS = Decimal("0.01")
_EMPTY = "—"


def money(value: Decimal | int | float | None) -> str:
    """1234567.891 -> '1 234 567,89' (polski zapis, twarda spacja jako separator tysięcy)."""
    if value is None:
        return _EMPTY
    amount = Decimal(value).quantize(_CENTS, rounding=ROUND_HALF_UP)
    return f"{amount:,.2f}".replace(",", " ").replace(".", ",")


def pct(value: Decimal | float | None, digits: int = 1) -> str:
    """0.4567 -> '45,7%'."""
    if value is None:
        return _EMPTY
    return f"{Decimal(value) * 100:.{digits}f}%".replace(".", ",")


def local_dt(value: datetime | None, fmt: str = "%d.%m.%Y %H:%M") -> str:
    """Czas z bazy (UTC, zwykle bez strefy) -> czas polski."""
    if value is None:
        return _EMPTY
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(APP_TIMEZONE).strftime(fmt)


def register(env) -> None:
    env.filters["money"] = money
    env.filters["pct"] = pct
    env.filters["local_dt"] = local_dt
