from contract_costs.services.common.resolve_utils import normalize_bank_account


def test_normalize_bank_account_strips_spaces_and_prefix():
    assert normalize_bank_account(
        "PL 12 3456 7890 1234 5678 9012 3456"
    ) == "12345678901234567890123456"



def test_normalize_bank_account_invalid_length_returns_none():
    assert normalize_bank_account("123") is None


def test_normalize_bank_account_invalid_chars_returns_none():
    assert normalize_bank_account("PL ABC") is None
