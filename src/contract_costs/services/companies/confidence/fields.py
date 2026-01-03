from enum import Enum

COMPANY_FIELDS = {
    "name",
    "tax_number",
    "address",
    "contact",
    "bank_account",
}


class CompanyField(Enum):
    TAX_NUMBER = "tax_number"
    BANK_ACCOUNT = "bank_account"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"

    NAME = "name"
    STREET = "street"
    ZIP_CODE = "zip_code"
    CITY = "city"
    COUNTRY = "country"

class CompanyDataSource(Enum):
    OCR = "ocr"
    EXCEL = "excel"
    API = "api"
    MANUAL = "manual"
    SYSTEM = "system"


class CompanyQualityFields:
    def __init__(self, values: dict[CompanyField, str | None]):
        self._values = values

    def get(self, field: CompanyField) -> str | None:
        return self._values.get(field)

    def has(self, field: CompanyField) -> bool:
        value = self.get(field)
        return value is not None and str(value).strip() != ""
