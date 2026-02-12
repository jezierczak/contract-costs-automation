from contract_costs.services.companies.normalize.name import normalize_company_name


def test_removes_sp_zoo():
    assert normalize_company_name("ACME Sp. z o.o.") == "ACME"

def test_keeps_core_name():
    assert normalize_company_name("ACME Transport") == "ACME TRANSPORT"

def test_handles_polish_chars():
    assert normalize_company_name("Żabka sp z o o") == "ŻABKA"