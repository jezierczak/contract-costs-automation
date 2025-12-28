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
