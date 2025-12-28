import re
from dataclasses import dataclass
from typing import Literal
from uuid import UUID
from enum import Enum

# CompanyTag = Literal[
#     "friendly",
#     "important",
#     "blacklisted",
#     "vip"
# ]

class CompanyType(Enum):
    OWN = "Own"
    COOPERATIVE = "Cooperative"
    OCCASIONAL = "Occasional"
    SUPPLIER = "Supplier"
    CLIENT = "Client"
    BUYER = "Buyer"
    SELLER = "Seller"

@dataclass(frozen=True)
class Address:
    street: str
    city: str
    zip_code: str
    country: str

    def __post_init__(self):
        country = self.country.strip().upper()
        if country in ("PL", "POLAND","POLSKA"):
            Address.check_polish_zip_code(self.zip_code)

    @staticmethod
    def check_polish_zip_code(zip_code: str) -> None:
        if not re.match(r"^\d{2}-\d{3}$", zip_code):
            raise ValueError("Invalid zip code")

@dataclass(frozen=True)
class Contact:
    phone_number: str
    email: str


@dataclass(frozen=True)
class BankAccount:
    number: str
    country_code: str | None = None

    def __post_init__(self):
        number = self.number.replace(" ", "")
        object.__setattr__(self, "number", number)

        if self.country_code:
            country_code = self.country_code.strip().upper()

            if len(country_code) != 2 or not country_code.isalpha():
                raise ValueError("Country code must be a 2-letter ISO code")

            object.__setattr__(self, "country_code", country_code)

            if country_code == "PL":
                if len(number) != 26 or not number.isdigit():
                    raise ValueError("Polish account number must have 26 digits")

    @property
    def iban(self) -> str | None:
        if not self.country_code:
            return None
        return f"{self.country_code}{self.number}"


@dataclass
class Company:
    id: UUID
    name: str
    description: str | None
    tax_number: str
    address: Address | None
    contact: Contact | None
    bank_account: BankAccount | None
    role: CompanyType
    tags: set[str] | None
    is_active: bool


