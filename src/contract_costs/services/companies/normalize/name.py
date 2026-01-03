import re

LEGAL_SUFFIXES = [
    "SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ",
    "SPOLKA Z OGRANICZONA ODPOWIEDZIALNOSCIA",
    "SPÓŁKA Z O O",
    "SP Z O O",
    "SP. Z O.O.",
    "SP Z O.O.",
    "SP ZOO",
    "SPÓŁKA JAWNA",
    "SP J",
    "SP.J.",
]

def normalize_company_name(name: str | None) -> str | None:
    if not name:
        return None

    value = name.upper()

    # usuń znaki specjalne
    value = re.sub(r"[^\w\s]", " ", value)

    # usuń formy prawne
    for suffix in LEGAL_SUFFIXES:
        value = value.replace(suffix, "")

    # normalizacja spacji
    value = re.sub(r"\s+", " ", value).strip()

    return value or None
