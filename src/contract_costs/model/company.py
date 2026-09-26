import logging
import re
from dataclasses import dataclass, field
from uuid import UUID
from enum import Enum

from contract_costs.model.base_entity import BaseEntity


logger = logging.getLogger(__name__)

class ReferenceNumberingMode(Enum):
    """Automatyczna numeracja dokumentów wystawianych w imieniu sprzedawcy (np. ZUS, US, bank)."""
    MONTHLY = "monthly"
    YEARLY = "yearly"
    GLOBAL = "global"


class CompanyVerificationStatus(Enum):
    """TO_VERIFY = firma założona z niepewnych danych (np. OCR bez poprawnego NIP-u) – do uzupełnienia przez użytkownika."""
    VERIFIED = "verified"
    TO_VERIFY = "to_verify"


class CompanyType(Enum):
    OWN = "Own"
    COOPERATIVE = "Cooperative"
    OCCASIONAL = "Occasional"
    SUPPLIER = "Supplier"
    CLIENT = "Client"
    BUYER = "Buyer"
    SELLER = "Seller"

@dataclass(frozen=True, slots=True)
class Address:
    street: str | None
    city: str | None
    zip_code: str | None
    country: str | None

    def __post_init__(self):
        if not self.country:
            return
        country = self.country.strip().upper()
        if country in ("PL", "POLAND","POLSKA"):
            if self.zip_code:
                Address.check_polish_zip_code(self.zip_code)

    @staticmethod
    def check_polish_zip_code(zip_code: str) -> None:
        if not re.match(r"^\d{2}-\d{3}$", zip_code):
            logger.warning(f"Invalid zip code: {zip_code}")
            # raise ValueError("Invalid zip code")

@dataclass(frozen=True, slots=True)
class Contact:
    phone_number: str | None
    email: str | None


@dataclass(frozen=True, slots=True)
class BankAccount:
    account_number: str | None
    country_code: str | None = None


    def __post_init__(self):
        if not self.account_number:
            object.__setattr__(self, "account_number", None)
            object.__setattr__(self, "country_code", None)
            return

        number = self.account_number.replace(" ", "")
        object.__setattr__(self, "account_number", number)

        if self.country_code:
            country_code = self.country_code.strip().upper()

            if len(country_code) != 2 or not country_code.isalpha():
                raise ValueError("Country code must be a 2-letter ISO code")

            object.__setattr__(self, "country_code", country_code)

            if country_code == "PL":
                if len(number) != 26 or not number.isdigit():
                    logger.warning(f"Polish account number must have 26 digits")
                    # raise ValueError("Polish account number must have 26 digits")

    @property
    def iban(self) -> str | None:
        if not self.country_code:
            return self.account_number
        return f"{self.country_code}{self.account_number}"


@dataclass(slots=True)
class Company(BaseEntity):
    id: UUID
    name: str
    description: str | None
    tax_number: str
    address: Address | None
    contact: Contact | None
    bank_account: BankAccount | None
    role: CompanyType
    is_active: bool
    tags: set[str] = field(default_factory=set)
    # None = numer wpisywany ręcznie
    reference_numbering_mode: ReferenceNumberingMode | None = None
    verification_status: CompanyVerificationStatus = CompanyVerificationStatus.VERIFIED


