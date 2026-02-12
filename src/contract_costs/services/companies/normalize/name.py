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
    "S.A.",
    "S A",
    "SA,"
    "SPK",
    "SPÓŁKA KOMANDYTOWA"
]

# prekompilacja wzorca
LEGAL_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(s) for s in LEGAL_SUFFIXES) + r")\b",
)

def normalize_company_name(name: str | None) -> str | None:
    if not name:
        return None

    value = name.upper()

    # 1️⃣ usuń znaki specjalne
    value = re.sub(r"[^\w\s]", " ", value)

    # 2️⃣ normalizacja spacji
    value = re.sub(r"\s+", " ", value).strip()

    # 3️⃣ usuń formy prawne
    value = LEGAL_PATTERN.sub("", value)

    # 4️⃣ finalne czyszczenie
    value = re.sub(r"\s+", " ", value).strip()

    return value or None
