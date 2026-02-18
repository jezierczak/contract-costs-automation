from types import SimpleNamespace
from uuid import uuid4

import pytest

from contract_costs.services.common.resolve_utils import (
    normalize_bank_account,
    normalize_phone,
    normalize_required_tax_number,
    normalize_tax_number,
    resolve_or_none,
)


def test_resolve_or_none_returns_none_for_empty_code() -> None:
    assert resolve_or_none(lambda *_: None, uuid4(), None, "ValueType") is None
    assert resolve_or_none(lambda *_: None, uuid4(), "", "ValueType") is None


def test_resolve_or_none_returns_entity_id() -> None:
    entity_id = uuid4()
    org_id = uuid4()
    captured = {}

    def _getter(org, code):
        captured["org"] = org
        captured["code"] = code
        return SimpleNamespace(id=entity_id)

    result = resolve_or_none(_getter, org_id, "VT-1", "ValueType")
    assert result == entity_id
    assert captured["org"] == str(org_id)
    assert captured["code"] == "VT-1"


def test_resolve_or_none_raises_when_not_found() -> None:
    with pytest.raises(ValueError, match="ValueType not found"):
        resolve_or_none(lambda *_: None, uuid4(), "VT-1", "ValueType")


def test_normalize_tax_number_handles_prefix_and_symbols() -> None:
    assert normalize_tax_number("PL 676-268-01-95") == "6762680195"
    assert normalize_tax_number("  ") is None
    assert normalize_tax_number(None) is None
    assert normalize_tax_number(6762680195) == "6762680195"


def test_normalize_required_tax_number_supports_tmp_ai_and_raises_for_missing() -> None:
    assert normalize_required_tax_number("TMP-123") == "TMP-123"
    assert normalize_required_tax_number("AI-abc") == "AI-abc"
    assert normalize_required_tax_number("PL 676-268-01-95") == "6762680195"

    with pytest.raises(ValueError, match="Tax number is required"):
        normalize_required_tax_number(" ")


def test_normalize_bank_account_validates_polish_format() -> None:
    assert normalize_bank_account("PL 65 1030 1188 0000 0000 5983 0200") == "65103011880000000059830200"
    assert normalize_bank_account("65-1030-1188-0000-0000-5983-0200") == "65103011880000000059830200"
    assert normalize_bank_account("abc") is None
    assert normalize_bank_account("123") is None


def test_normalize_phone_accepts_nine_digits_and_strips_polish_prefix() -> None:
    assert normalize_phone("+48 123-456-789") == "123456789"
    assert normalize_phone("123456789") == "123456789"
    assert normalize_phone("abc") is None
    assert normalize_phone("123") is None

