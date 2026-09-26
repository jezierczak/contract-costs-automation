import json
import re
import urllib.error
import urllib.request
from datetime import date

WHITELIST_URL = "https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={date}"

_ZIP_CITY = re.compile(r"^(?P<street>.*?),?\s*(?P<zip>\d{2}-\d{3})\s+(?P<city>.+)$")


_ROMAN_NUMERAL = re.compile(r"^(?=..)X{0,3}(IX|IV|V?I{0,3})$")

_LEGAL_FORMS = {
    "Sp. Z O.o.": "Sp. z o.o.",
}

# skróty form prawnych (PL i zagraniczne z VIES), które nie mają być "Pierwsza wielka"
_WORD_FORMS = {
    form.upper(): form
    for form in ("S.A.", "GmbH", "AG", "KG", "BV", "B.V.", "NV", "N.V.", "SRL", "S.R.L.",
                 "SAS", "SARL", "S.L.", "SL", "Ltd", "Ltd.", "LLC", "s.r.o.", "a.s.", "UAB", "OÜ", "AB", "ApS", "A/S")
}


def _capitalize_word(word: str) -> str:
    if _ROMAN_NUMERAL.match(word):
        return word
    if word.upper() in _WORD_FORMS:
        return _WORD_FORMS[word.upper()]
    return "-".join(part.capitalize() for part in word.split("-"))


def normalize_case(text: str) -> str:
    """
    Biała Lista zwraca dane WIELKIMI LITERAMI – zamienia je na "Pierwsza wielka, reszta małe"
    w każdym słowie (także po myślniku), zostawiając liczby rzymskie i typowe formy prawne.
    """
    result = " ".join(_capitalize_word(word) for word in text.split())
    for wrong, right in _LEGAL_FORMS.items():
        result = result.replace(wrong, right)
    return result


def parse_whitelist_address(address: str | None) -> dict:
    """
    Biała Lista zwraca adres jednym ciągiem, np. "UL. KRAKOWSKA 10, 30-001 KRAKÓW".
    Rozbija go na ulicę, kod i miasto; gdy format nie pasuje, całość trafia do ulicy.
    """
    if not address:
        return {"street": "", "zip_code": "", "city": ""}

    match = _ZIP_CITY.match(address.strip())
    if not match:
        return {"street": address.strip(), "zip_code": "", "city": ""}

    return {
        "street": match.group("street").strip(),
        "zip_code": match.group("zip"),
        "city": match.group("city").strip(),
    }


def lookup_company_by_nip(nip: str, timeout: float = 5.0) -> dict | None:
    """
    Szuka podmiotu po NIP-ie w Białej Liście MF (wl-api.mf.gov.pl, bez klucza API).
    Zwraca nazwę i adres albo None, gdy NIP jest błędny, podmiotu nie ma lub API nie odpowiada.
    """
    nip = re.sub(r"\D", "", nip or "")
    if len(nip) != 10:
        return None

    url = WHITELIST_URL.format(nip=nip, date=date.today().isoformat())
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            payload = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None

    subject = (payload.get("result") or {}).get("subject")
    if not subject:
        return None

    address = subject.get("workingAddress") or subject.get("residenceAddress")
    fields = {"name": subject.get("name") or "", **parse_whitelist_address(address)}
    return {**{key: normalize_case(value) for key, value in fields.items()}, "country": "Polska"}
