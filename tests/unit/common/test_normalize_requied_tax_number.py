import pytest

from contract_costs.services.common.resolve_utils import normalize_required_tax_number


def test_required_tax_number_allows_tmp_prefix():
    assert normalize_required_tax_number("TMP-001") == "TMP-001"


def test_required_tax_number_allows_ai_prefix():
    assert normalize_required_tax_number("AI-XYZ") == "AI-XYZ"


def test_required_tax_number_normalizes_regular_value():
    assert normalize_required_tax_number("PL 123-456-32-18") == "1234563218"


def test_required_tax_number_raises_when_missing():
    with pytest.raises(ValueError):
        normalize_required_tax_number(None)
