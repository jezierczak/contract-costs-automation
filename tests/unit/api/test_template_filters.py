from datetime import datetime, timezone
from decimal import Decimal

from api.template_filters import local_dt, money, pct


def test_money_formats_polish_style():
    assert money(Decimal("1234567.891")) == "1 234 567,89"
    assert money(Decimal("-50")) == "-50,00"
    assert money(None) == "—"


def test_pct():
    assert pct(Decimal("0.4567")) == "45,7%"
    assert pct(None) == "—"


def test_local_dt_converts_utc_to_polish_time():
    assert local_dt(datetime(2026, 9, 26, 10, 5)) == "26.09.2026 12:05"
    assert local_dt(datetime(2026, 1, 5, 23, 30, tzinfo=timezone.utc)) == "06.01.2026 00:30"
    assert local_dt(None) == "—"

