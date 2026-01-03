import re
from dataclasses import replace

from contract_costs.model.company import Company, Contact, BankAccount
from contract_costs.services.common.resolve_utils import normalize_tax_number


class CompanyNormalizeService:

    def normalize(self, company: Company) -> Company:
        contact = None
        if company.contact:
            phone = self.normalize_phone(company.contact.phone_number)
            email = self.normalize_email(company.contact.email)
            if phone or email:
                contact = Contact(phone_number=phone, email=email)

        bank_account = None
        if company.bank_account:
            number = self.normalize_bank_account(company.bank_account.number)
            if number:
                bank_account = BankAccount(
                    number=number,
                    country_code=company.bank_account.country_code,
                )
        # 🔥 KLUCZOWE: normalizujemy tax_number TYLKO jeśli istnieje
        if company.tax_number is not None:
            normalized_tax = self._normalize_tax_number_company(company.tax_number)
        else:
            normalized_tax = company.tax_number  # None zostaje None
        return replace(
            company,
            tax_number=normalized_tax,
            contact=contact,
            bank_account=bank_account,
        )

    @staticmethod
    def _normalize_tax_number_company(value: str) -> str:
        if value.startswith("TMP-"):
            return value
        normalized = normalize_tax_number(value)
        if not normalized:
            raise ValueError(f"Invalid tax_number in Company: {value}")
        return normalized

    @staticmethod
    def normalize_tax_number(value: str | None) -> str | None:
        if not value:
            return None
        if value.startswith("TMP-"):
            return value
        return normalize_tax_number(value) or ""

    @staticmethod
    def normalize_bank_account(value: str | None) -> str | None:
        if not value:
            return None
        value = value.replace(" ", "").replace("-", "")
        if value.startswith("PL"):
            value = value.replace("PL", "")
        return value.upper()

    @staticmethod
    def normalize_phone(phone: str | None) -> str | None:
        if not phone:
            return None

        # zamieniamy wszystko na separatory
        cleaned = re.sub(r"[()\s\-]", "", phone)

        # wszystkie potencjalne ciągi cyfr
        candidates = re.findall(r"\d{7,15}", cleaned)


        for raw in candidates:
            if len(raw) >= 9:
                return raw

        return None


    @staticmethod
    def normalize_email(value: str | None) -> str | None:
        return value.strip().lower() if value else None

