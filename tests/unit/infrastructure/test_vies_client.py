import io
import json

import pytest

from contract_costs.infrastructure import vies_client
from contract_costs.infrastructure.vies_client import (
    ViesUnavailableError,
    lookup_company_by_vat_number,
    parse_vies_address,
)


def test_parse_address_splits_last_line_into_zip_and_city():
    assert parse_vies_address("MUSTERSTRASSE 1\n12345 BERLIN") == {
        "street": "Musterstrasse 1",
        "zip_code": "12345",
        "city": "Berlin",
    }


def test_parse_address_keeps_mixed_case_when_last_line_has_no_zip():
    result = parse_vies_address("Gordon House\nBarrow Street\nDublin 4")

    assert result == {"street": "Gordon House, Barrow Street, Dublin 4", "zip_code": "", "city": ""}


def test_parse_address_hidden():
    assert parse_vies_address("---") == {"street": "", "zip_code": "", "city": ""}
    assert parse_vies_address(None) == {"street": "", "zip_code": "", "city": ""}


def _fake_urlopen(payload, calls):
    def urlopen(url, timeout):
        calls.append(url)
        return io.BytesIO(json.dumps(payload).encode())
    return urlopen


def test_lookup_returns_company_data(monkeypatch):
    calls = []
    payload = {"isValid": True, "userError": "VALID", "name": "MUSTER GMBH",
               "address": "MUSTERSTRASSE 1\n12345 BERLIN"}
    monkeypatch.setattr(vies_client.urllib.request, "urlopen", _fake_urlopen(payload, calls))

    assert lookup_company_by_vat_number("DE 123 456 789") == {
        "name": "Muster GmbH",
        "street": "Musterstrasse 1",
        "zip_code": "12345",
        "city": "Berlin",
        "country": "Niemcy",
    }
    assert calls[0].endswith("/ms/DE/vat/123456789")


def test_lookup_hidden_name_and_address_gives_empty_fields(monkeypatch):
    payload = {"isValid": True, "userError": "VALID", "name": "---", "address": "---"}
    monkeypatch.setattr(vies_client.urllib.request, "urlopen", _fake_urlopen(payload, []))

    result = lookup_company_by_vat_number("DE123456789")

    assert result["name"] == "" and result["street"] == ""
    assert result["country"] == "Niemcy"


def test_lookup_maps_gr_to_el(monkeypatch):
    calls = []
    payload = {"isValid": True, "name": "X", "address": "Y"}
    monkeypatch.setattr(vies_client.urllib.request, "urlopen", _fake_urlopen(payload, calls))

    lookup_company_by_vat_number("GR123456789")

    assert "/ms/EL/vat/123456789" in calls[0]


def test_lookup_invalid_number_returns_none(monkeypatch):
    payload = {"isValid": False, "userError": "INVALID"}
    monkeypatch.setattr(vies_client.urllib.request, "urlopen", _fake_urlopen(payload, []))

    assert lookup_company_by_vat_number("DE000000000") is None


def test_lookup_unknown_country_does_not_call_api(monkeypatch):
    calls = []
    monkeypatch.setattr(vies_client.urllib.request, "urlopen", _fake_urlopen({}, calls))

    assert lookup_company_by_vat_number("US123456789") is None
    assert calls == []


def test_lookup_member_state_unavailable_raises(monkeypatch):
    payload = {"isValid": False, "userError": "MS_UNAVAILABLE"}
    monkeypatch.setattr(vies_client.urllib.request, "urlopen", _fake_urlopen(payload, []))

    with pytest.raises(ViesUnavailableError):
        lookup_company_by_vat_number("DE123456789")


def test_lookup_network_error_raises(monkeypatch):
    def failing(url, timeout):
        raise vies_client.urllib.error.URLError("down")
    monkeypatch.setattr(vies_client.urllib.request, "urlopen", failing)

    with pytest.raises(ViesUnavailableError):
        lookup_company_by_vat_number("DE123456789")
