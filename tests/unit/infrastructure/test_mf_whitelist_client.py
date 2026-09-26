import io
import json

from contract_costs.infrastructure import mf_whitelist_client
from contract_costs.infrastructure.mf_whitelist_client import (
    lookup_company_by_nip,
    normalize_case,
    parse_whitelist_address,
)


def test_parse_address_splits_street_zip_and_city():
    assert parse_whitelist_address("UL. KRAKOWSKA 10, 30-001 KRAKÓW") == {
        "street": "UL. KRAKOWSKA 10",
        "zip_code": "30-001",
        "city": "KRAKÓW",
    }


def test_parse_address_handles_multi_word_city():
    result = parse_whitelist_address("DŁUGA 5/2, 05-500 PIASECZNO-JÓZEFOSŁAW NOWY")
    assert result["zip_code"] == "05-500"
    assert result["city"] == "PIASECZNO-JÓZEFOSŁAW NOWY"


def test_parse_address_without_zip_keeps_whole_string_as_street():
    assert parse_whitelist_address("JAKIŚ DZIWNY ADRES") == {
        "street": "JAKIŚ DZIWNY ADRES",
        "zip_code": "",
        "city": "",
    }


def test_parse_address_empty():
    assert parse_whitelist_address(None) == {"street": "", "zip_code": "", "city": ""}


def _fake_urlopen(payload, calls):
    def urlopen(url, timeout):
        calls.append(url)
        return io.BytesIO(json.dumps(payload).encode())
    return urlopen


def test_lookup_returns_name_and_working_address(monkeypatch):
    calls = []
    payload = {"result": {"subject": {
        "name": "FIRMA SP. Z O.O.",
        "workingAddress": "UL. KRAKOWSKA 10, 30-001 KRAKÓW",
        "residenceAddress": None,
    }}}
    monkeypatch.setattr(mf_whitelist_client.urllib.request, "urlopen", _fake_urlopen(payload, calls))

    result = lookup_company_by_nip("PL 123-456-32-18")

    assert result == {
        "name": "Firma Sp. z o.o.",
        "street": "Ul. Krakowska 10",
        "zip_code": "30-001",
        "city": "Kraków",
        "country": "Polska",
    }
    assert "/nip/1234563218?" in calls[0]


def test_lookup_falls_back_to_residence_address(monkeypatch):
    payload = {"result": {"subject": {
        "name": "JAN KOWALSKI",
        "workingAddress": None,
        "residenceAddress": "LIPOWA 1, 00-001 WARSZAWA",
    }}}
    monkeypatch.setattr(mf_whitelist_client.urllib.request, "urlopen", _fake_urlopen(payload, []))

    assert lookup_company_by_nip("1234563218")["city"] == "Warszawa"


def test_lookup_returns_none_when_subject_missing(monkeypatch):
    payload = {"result": {"subject": None}}
    monkeypatch.setattr(mf_whitelist_client.urllib.request, "urlopen", _fake_urlopen(payload, []))

    assert lookup_company_by_nip("1234563218") is None


def test_lookup_rejects_invalid_nip_without_calling_api(monkeypatch):
    calls = []
    monkeypatch.setattr(mf_whitelist_client.urllib.request, "urlopen", _fake_urlopen({}, calls))

    assert lookup_company_by_nip("123") is None
    assert lookup_company_by_nip("OTH-000001") is None
    assert calls == []


def test_lookup_returns_none_on_network_error(monkeypatch):
    def failing(url, timeout):
        raise mf_whitelist_client.urllib.error.URLError("down")
    monkeypatch.setattr(mf_whitelist_client.urllib.request, "urlopen", failing)

    assert lookup_company_by_nip("1234563218") is None


def test_normalize_case_capitalizes_each_word():
    assert normalize_case("ORLEN SPÓŁKA AKCYJNA") == "Orlen Spółka Akcyjna"
    assert normalize_case("BIELSKO-BIAŁA") == "Bielsko-Biała"


def test_normalize_case_keeps_legal_forms_and_roman_numerals():
    assert normalize_case("BUDREMEX SP. Z O.O.") == "Budremex Sp. z o.o."
    assert normalize_case("FIRMA S.A.") == "Firma S.A."
    assert normalize_case("AL. JANA PAWŁA II 12/3") == "Al. Jana Pawła II 12/3"
    assert normalize_case("JAN I SYN") == "Jan I Syn"


def test_normalize_case_keeps_foreign_legal_forms():
    assert normalize_case("MUSTER GMBH") == "Muster GmbH"
    assert normalize_case("AGRO HANDEL AG") == "Agro Handel AG"
