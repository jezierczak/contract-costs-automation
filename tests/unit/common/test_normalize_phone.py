from contract_costs.services.common.resolve_utils import normalize_phone


def test_normalize_phone_removes_country_prefix():
    assert normalize_phone("+48 600 700 800") == "600700800"


def test_normalize_phone_invalid_returns_none():
    assert normalize_phone("123") is None


def test_normalize_phone_strips_non_digits():
    assert normalize_phone("600-700-800") == "600700800"
