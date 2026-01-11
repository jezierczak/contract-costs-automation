from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from contract_costs.model.company import CompanyType


class CompanyActionType(Enum):
    NONE = "none"
    CREATE = "create"
    UPDATE = "update"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"




@dataclass(frozen=True)
class CompanyActionCommand:
    # =====================
    # ACTION
    # =====================
    action: CompanyActionType

    # =====================
    # IDENTYFIKACJA
    # =====================
    company_id: UUID | None
    tax_number: str

    # =====================
    # DANE PODSTAWOWE
    # =====================
    name: str
    role: CompanyType
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

    # =====================
    # TAGS
    # =====================
    tags: set[str]