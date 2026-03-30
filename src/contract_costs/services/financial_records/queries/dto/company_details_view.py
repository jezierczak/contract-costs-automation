from dataclasses import dataclass


@dataclass(frozen=True,slots=True)
class CompanyDetailsView:
    name: str
    tax_number: str

    street: str | None
    city: str | None
    zip_code: str | None
    country: str | None

    email: str | None
    phone: str | None

    bank_account: str | None
    iban: str | None