from decimal import Decimal

from api.template_filters import money, pct


def test_money_formats_polish_style():
    assert money(Decimal("1234567.891")) == "1 234 567,89"
    assert money(Decimal("-50")) == "-50,00"
    assert money(None) == "—"


def test_pct():
    assert pct(Decimal("0.4567")) == "45,7%"
    assert pct(None) == "—"
