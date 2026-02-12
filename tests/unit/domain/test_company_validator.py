from contract_costs.services.companies.validators.company import CompanyValidator


def test_valid_nip():
    # poprawny NIP (przechodzi checksum)
    assert CompanyValidator.validate_nip("1234563218") is True


def test_valid_nip_with_prefix_and_spaces():
    assert CompanyValidator.validate_nip("PL 123-456-32-18") is True


def test_invalid_checksum():
    assert CompanyValidator.validate_nip("1234563219") is False


def test_invalid_length():
    assert CompanyValidator.validate_nip("123") is False
    assert CompanyValidator.validate_nip("1234567890123") is False


def test_none_returns_false():
    assert CompanyValidator.validate_nip(None) is False


def test_empty_string_returns_false():
    assert CompanyValidator.validate_nip("") is False
