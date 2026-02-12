from contract_costs.services.common.resolve_utils import normalize_tax_number


def test_normalize_tax_number_removes_prefix_and_non_digits():
    assert normalize_tax_number("PL 123-456-32-18") == "1234563218"


def test_normalize_tax_number_handles_int():
    assert normalize_tax_number(1234567890) == "1234567890"


def test_normalize_tax_number_empty_returns_none():
    assert normalize_tax_number("") is None


def test_normalize_tax_number_none_returns_none():
    assert normalize_tax_number(None) is None
