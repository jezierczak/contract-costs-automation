import re
from uuid import UUID


def resolve_or_none(getter, code: str | None, label: str) -> UUID | None:
    """
    getter: repo.get_by_code
    code: np. 'TAUR'
    label: nazwa encji do komunikatu błędu
    """

    if not code:
        return None

    entity = getter(code)
    if entity is None:
        raise ValueError(f"{label} not found for code: {code}")

    return entity.id



def normalize_tax_number(nip: str | int | None) -> str | None:
    if nip is None:
        return None

    # rzutuj wszystko na string
    nip = str(nip).strip()

    if not nip:
        return None

    # usuń prefix PL (na początku)
    nip = re.sub(r'^PL\s*', '', nip, flags=re.IGNORECASE)

    # usuń WSZYSTKO poza cyframi
    nip = re.sub(r'\D', '', nip)

    # opcjonalna walidacja długości
    # if len(nip) != 10:
    #     return None  # albo raise ValueError

    return nip

def normalize_required_tax_number(nip: str | int | None) -> str:
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
