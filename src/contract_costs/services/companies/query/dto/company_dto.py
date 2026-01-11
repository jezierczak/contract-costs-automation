from dataclasses import dataclass
from uuid import UUID

from contract_costs.model.company import CompanyType


@dataclass(frozen=True)
class CompanyDTO:
    # =====================
    # IDENTYFIKACJA
    # =====================
    id: UUID
    name: str
    tax_number: str

    # =====================
    # BIZNES
    # =====================
    role: CompanyType
    is_active: bool
    tags: set[str]
    # =====================
    # OPIS
    # =====================
    description: str | None

    # =====================
    # ADRES
    # =====================
    address_street: str | None
    address_city: str | None
    address_zip_code: str | None
    address_country: str | None

    # =====================
    # KONTAKT
    # =====================
    phone_number: str | None
    email: str | None

    # =====================
    # BANK
    # =====================
    bank_account_number: str | None
    bank_account_country_code: str | None
    iban: str | None

    # =====================
    # READ METADATA
    # =====================
    quality_score: int | None = None
