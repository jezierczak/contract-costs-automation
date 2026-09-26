import re
from uuid import UUID


def resolve_or_none(getter,organization_id: UUID, code: str | None, label: str) -> UUID | None:
    """
    getter: repo.get_by_code
    code: np. 'TAUR'
    label: nazwa encji do komunikatu błędu
    """

    if not code:
        return None

    entity = getter(str(organization_id),code)
    if entity is None:
        raise ValueError(f"{label} not found for code: {code}")

    return entity.id



# identyfikatory firm, które nie są NIP-em – zostają w bazie w niezmienionej postaci
OTHER_IDENTIFIER_PREFIX = "OTH-"          # nadawany ręcznie (przycisk „Generuj numer”)
LEGACY_PLACEHOLDER_PREFIXES = ("TMP-", "AI-")
UNKNOWN_SELLER_ID = "UNKNOWN_SELLER"      # wspólna firma dla nierozpoznanych sprzedawców
UNKNOWN_BUYER_ID = "UNKNOWN_BUYER"        # wspólna firma dla nierozpoznanych nabywców
UNKNOWN_COMPANY_IDS = (UNKNOWN_SELLER_ID, UNKNOWN_BUYER_ID)


def is_placeholder_identifier(value: str | None) -> bool:
    if not value:
        return False
    value = value.strip()
    return (
        value.startswith((OTHER_IDENTIFIER_PREFIX, *LEGACY_PLACEHOLDER_PREFIXES))
        or value in UNKNOWN_COMPANY_IDS
    )


# etykieta dopisana przez OCR/AI, np. "NIP: 123-456-78-90" (żaden kod kraju UE nie zaczyna się od N ani V)
_TAX_NUMBER_LABEL = re.compile(r'^(NIP|VAT\s*(ID)?)\s*:?\s*', flags=re.IGNORECASE)


def normalize_tax_number(nip: str | int | None) -> str | None:
    """
    Polski NIP → same cyfry ("PL 123-456-78-90" → "1234567890").
    Numer zagraniczny zachowuje litery ("DE 123 456 789" → "DE123456789",
    "NL123456789B01", "ATU12345678") — usuwamy tylko separatory.
    """
    if nip is None:
        return None

    # rzutuj wszystko na string
    nip = str(nip).strip()

    if not nip:
        return None

    nip = _TAX_NUMBER_LABEL.sub('', nip)

    # zostają tylko litery i cyfry (spacje, myślniki, kropki, ukośniki znikają)
    nip = re.sub(r'[^0-9A-Za-z]', '', nip).upper()

    # każdy numer podatkowy (NIP, VAT UE) ma cyfry — same litery to śmieć
    if not any(ch.isdigit() for ch in nip):
        return None

    # prefiks PL zdejmujemy tylko z polskiego NIP-u (po nim same cyfry)
    if nip.startswith('PL') and nip[2:].isdigit():
        nip = nip[2:]

    return nip

def normalize_required_tax_number(nip: str | int | None) -> str:
    if isinstance(nip,str):
        value = nip.strip()
        if is_placeholder_identifier(value):
            return value  # 🔥 KLUCZ

    normalized = normalize_tax_number(nip)
    if normalized is None:
        raise ValueError("Tax number is required")
    return normalized


def normalize_bank_account(account: str | None) -> str | None:
    if not account:
        return None

    value = account.strip().upper()

    # usuwamy spacje i myślniki
    value = re.sub(r"[\s\-]", "", value)

    # usuwamy prefix PL
    if value.startswith("PL"):
        value = value[2:]

    # tylko cyfry
    if not value.isdigit():
        return None

    # polskie konto = 26 cyfr
    if len(value) != 26:
        return None

    return value

def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None

    # tylko cyfry
    digits = re.sub(r"\D", "", phone)

    if not digits:
        return None

    # prefix PL
    if digits.startswith("48") and len(digits) > 9:
        digits = digits[2:]

    # polski numer = 9 cyfr
    if len(digits) != 9:
        return None

    return digits
