import json
import re
import urllib.error
import urllib.request

from contract_costs.infrastructure.mf_whitelist_client import normalize_case

VIES_URL = "https://ec.europa.eu/taxation_customs/vies/rest-api/ms/{country}/vat/{number}"

# kody VIES (Grecja = EL, Irlandia Płn. = XI) → nazwa kraju jak w formularzu firmy
EU_COUNTRIES = {
    "AT": "Austria", "BE": "Belgia", "BG": "Bułgaria", "CY": "Cypr", "CZ": "Czechy",
    "DE": "Niemcy", "DK": "Dania", "EE": "Estonia", "EL": "Grecja", "ES": "Hiszpania",
    "FI": "Finlandia", "FR": "Francja", "HR": "Chorwacja", "HU": "Węgry", "IE": "Irlandia",
    "IT": "Włochy", "LT": "Litwa", "LU": "Luksemburg", "LV": "Łotwa", "MT": "Malta",
    "NL": "Holandia", "PL": "Polska", "PT": "Portugalia", "RO": "Rumunia", "SE": "Szwecja",
    "SI": "Słowenia", "SK": "Słowacja", "XI": "Irlandia Północna",
}

# VIES zwraca "---", gdy kraj nie udostępnia nazwy/adresu (np. Niemcy, Hiszpania)
_HIDDEN = {"", "---"}


class ViesUnavailableError(Exception):
    """VIES albo system kraju członkowskiego chwilowo nie odpowiada."""


def _tidy(text: str) -> str:
    text = " ".join(text.split())
    return normalize_case(text) if text.isupper() else text


def parse_vies_address(address: str | None) -> dict:
    """
    Adres z VIES to kilka linii w formacie kraju, np. "MUSTERSTR. 1\n12345 BERLIN".
    Ostatnia linia zaczynająca się od kodu (token z cyfrą) → kod + miasto, reszta → ulica.
    """
    lines = [line.strip() for line in re.split(r"[\n,]", address or "") if line.strip()]
    if not lines or " ".join(lines) in _HIDDEN:
        return {"street": "", "zip_code": "", "city": ""}

    zip_code, city = "", ""
    last = lines[-1].split(maxsplit=1)
    if len(lines) > 1 and len(last) == 2 and any(ch.isdigit() for ch in last[0]):
        zip_code, city = last
        lines = lines[:-1]

    return {"street": _tidy(", ".join(lines)), "zip_code": zip_code, "city": _tidy(city)}


def lookup_company_by_vat_number(vat_number: str, timeout: float = 10.0) -> dict | None:
    """
    Sprawdza numer VAT UE w VIES (bez klucza API). Numer musi zaczynać się od kodu kraju.
    Zwraca dane firmy (puste nazwa/adres, gdy kraj ich nie udostępnia) albo None dla numeru nieaktywnego.
    Rzuca ViesUnavailableError, gdy VIES lub system kraju nie odpowiada.
    """
    vat_number = re.sub(r"[^0-9A-Za-z]", "", vat_number or "").upper()
    country, number = vat_number[:2], vat_number[2:]
    if country == "GR":
        country = "EL"
    if country not in EU_COUNTRIES or not number:
        return None

    url = VIES_URL.format(country=country, number=number)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError) as e:
        raise ViesUnavailableError(str(e)) from e

    if not payload.get("isValid"):
        if payload.get("userError") not in (None, "VALID", "INVALID", "INVALID_INPUT"):
            raise ViesUnavailableError(payload.get("userError"))
        return None

    name = (payload.get("name") or "").strip()
    return {
        "name": "" if name in _HIDDEN else _tidy(name),
        **parse_vies_address(payload.get("address")),
        "country": EU_COUNTRIES[country],
    }
