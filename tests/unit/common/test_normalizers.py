from contract_costs.services.common.resolve_utils import normalize_tax_number


def test_normalize_tax_number_removes_prefix_and_non_digits():
    assert normalize_tax_number("PL 123-456-32-18") == "1234563218"


def test_normalize_tax_number_handles_int():
    assert normalize_tax_number(1234567890) == "1234567890"


def test_normalize_tax_number_empty_returns_none():
    assert normalize_tax_number("") is None


def test_normalize_tax_number_none_returns_none():
    assert normalize_tax_number(None) is None


def test_normalize_tax_number_keeps_letters_of_foreign_vat_numbers():
    assert normalize_tax_number("DE 123 456 789") == "DE123456789"
    assert normalize_tax_number("ATU12345678") == "ATU12345678"
    assert normalize_tax_number("nl123456789b01") == "NL123456789B01"
    assert normalize_tax_number("IE-1234567-T") == "IE1234567T"


def test_normalize_tax_number_strips_pl_prefix_only_from_polish_nip():
    assert normalize_tax_number("pl1234563218") == "1234563218"
    assert normalize_tax_number("PL.123.456.32.18") == "1234563218"


def test_normalize_tax_number_strips_ocr_label():
    assert normalize_tax_number("NIP: 123-456-32-18") == "1234563218"
    assert normalize_tax_number("VAT ID: DE123456789") == "DE123456789"


def test_normalize_tax_number_ksef_eu_code_with_number():
    # KSeF: KodUE + NrVatUE sklejane w parserze
    assert normalize_tax_number("CZ" + "12345678") == "CZ12345678"


def test_normalize_tax_number_only_separators_returns_none():
    assert normalize_tax_number(" - . ") is None


def test_normalize_tax_number_without_digits_returns_none():
    assert normalize_tax_number("INVALID") is None
