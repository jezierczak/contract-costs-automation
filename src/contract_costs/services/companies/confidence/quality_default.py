import logging
import re
from typing import Mapping

from contract_costs.model.company import Company
from contract_costs.services.companies.confidence.fields import (
    CompanyField,
    CompanyDataSource, CompanyQualityFields,
)
from contract_costs.services.companies.confidence.quality import CompanyDataQuality
from contract_costs.services.companies.validators.company import CompanyValidator
from contract_costs.services.invoices.dto.parse import CompanyInput

logger = logging.getLogger(__name__)

FIELD_WEIGHTS: dict[CompanyField, float] = {
    # 🔴 identyfikatory
    CompanyField.TAX_NUMBER: 0.22,
    CompanyField.BANK_ACCOUNT: 0.22,
    CompanyField.EMAIL: 0.15,
    CompanyField.PHONE_NUMBER: 0.10,

    # 🟡 adres
    CompanyField.STREET: 0.07,
    CompanyField.ZIP_CODE: 0.10,
    CompanyField.CITY: 0.05,
    CompanyField.COUNTRY: 0.02,

    # 🟢 opis
    CompanyField.NAME: 0.07,
}


class DefaultCompanyQuality(CompanyDataQuality):
    def __init__(
        self,
        fields: CompanyQualityFields,
        source: CompanyDataSource,
    ) -> None:
        self._fields = fields
        self._source = source
        self._field_scores = self._compute_field_scores()

    # ---------- factories ----------

    @classmethod
    def from_input(
        cls,
        input_: CompanyInput,
        source: CompanyDataSource | None = None,
    ) -> "DefaultCompanyQuality":
        return cls(
            CompanyQualityFields({
                CompanyField.NAME: input_.name,
                CompanyField.TAX_NUMBER: input_.tax_number,
                CompanyField.STREET: input_.street,
                CompanyField.CITY: input_.city,
                CompanyField.ZIP_CODE: input_.zip_code,
                CompanyField.COUNTRY: input_.country,
                CompanyField.PHONE_NUMBER: input_.phone_number,
                CompanyField.EMAIL: input_.email,
                CompanyField.BANK_ACCOUNT: input_.bank_account,
            }),
            source or CompanyDataSource.OCR,
        )

    @classmethod
    def from_company(
        cls,
        company: Company,
        source: CompanyDataSource | None = None,
    ) -> "DefaultCompanyQuality":
        return cls(
            CompanyQualityFields({
                CompanyField.NAME: company.name,
                CompanyField.TAX_NUMBER: company.tax_number,
                CompanyField.STREET: company.address.street if company.address else None,
                CompanyField.CITY: company.address.city if company.address else None,
                CompanyField.ZIP_CODE: company.address.zip_code if company.address else None,
                CompanyField.COUNTRY: company.address.country if company.address else None,
                CompanyField.PHONE_NUMBER: company.contact.phone_number if company.contact else None,
                CompanyField.EMAIL: company.contact.email if company.contact else None,
                CompanyField.BANK_ACCOUNT: (
                    company.bank_account.number if company.bank_account else None
                ),
            }),
            source or CompanyDataSource.SYSTEM,
        )

    # ---------- scoring ----------

    def _compute_field_scores(self) -> dict[CompanyField, int]:
        return {
            CompanyField.NAME: self._score_name(),
            CompanyField.TAX_NUMBER: self._score_tax_number(),
            CompanyField.STREET: self._score_street(),
            CompanyField.CITY: self._score_city(),
            CompanyField.ZIP_CODE: self._score_zip_code(),
            CompanyField.COUNTRY: self._score_country(),
            CompanyField.PHONE_NUMBER: self._score_phone(),
            CompanyField.EMAIL: self._score_email(),
            CompanyField.BANK_ACCOUNT: self._score_bank_account(),
        }

    # ---------- per-field scoring ----------

    def _score_name(self) -> int:
        value = self._fields.get(CompanyField.NAME)
        if not value:
            return 0

        upper = value.strip().upper()
        if upper.startswith("AI_") or upper in {"UNKNOWN", "N/A", "-", "?"}:
            return 0

        if len(upper) < 3:
            return 0

        if not re.search(r"[A-ZĄĆĘŁŃÓŚŻŹ]", upper):
            return 0

        normalized = re.sub(r"[\s\-.]", "", upper)
        return 100 if len(normalized) >= 6 else 50

    def _score_tax_number(self) -> int:
        return (
            100
            if CompanyValidator.validate_nip(
                self._fields.get(CompanyField.TAX_NUMBER)
            )
            else 0
        )

    def _score_street(self) -> int:
        value = self._fields.get(CompanyField.STREET)
        if not value or len(value.strip()) < 3:
            return 0
        return 100 if re.search(r"\d", value) else 50

    def _score_city(self) -> int:
        value = self._fields.get(CompanyField.CITY)
        if not value or len(value.strip()) < 3:
            return 0
        return 100

    def _score_zip_code(self) -> int:
        value = self._fields.get(CompanyField.ZIP_CODE)
        if not value:
            return 0
        if re.fullmatch(r"\d{2}-\d{3}", value):
            return 100
        digits = re.sub(r"\D", "", value)
        return 50 if len(digits) == 5 else 0

    def _score_country(self) -> int:
        value = self._fields.get(CompanyField.COUNTRY)
        if not value:
            return 0
        return 100 if value.upper() in {"PL", "POLSKA", "POLAND"} else 0

    def _score_phone(self) -> int:
        value = self._fields.get(CompanyField.PHONE_NUMBER)
        if not value:
            return 0
        digits = re.sub(r"\D", "", value)
        if digits.startswith("48"):
            digits = digits[2:]
        return 100 if len(digits) == 9 else 0

    def _score_email(self) -> int:
        value = self._fields.get(CompanyField.EMAIL)
        if not value or "@" not in value:
            return 0
        return 100 if re.fullmatch(r"[^@]+@[^@]+\.[^@]+", value) else 0

    def _score_bank_account(self) -> int:
        value = self._fields.get(CompanyField.BANK_ACCOUNT)
        if not value:
            return 0
        digits = re.sub(r"\D", "", value.replace("PL", ""))
        return 100 if len(digits) == 26 else 0

    # ---------- public API ----------

    def get_field_score(self, field: CompanyField) -> int:
        logger.info(f"Getting field score: {field} , score: {self._field_scores.get(field,0)}")
        return self._field_scores.get(field, 0)

    def get_field_scores(self) -> Mapping[str, int]:
        return {key.name:value for key,value in self._field_scores.items()}

    def get_overall_score(self) -> int:
        score = 0.0
        for field, weight in FIELD_WEIGHTS.items():
            score += self.get_field_score(field) * weight
        logger.info(f"Overall score: {int(round(score))}")
        return int(round(score))

    def get_value(self, field: CompanyField) -> str | None:
        return self._fields.get(field)

    def has_field(self, field: CompanyField) -> bool:
        value = self._fields.get(field)
        return value is not None and str(value).strip() != ""

    def get_source(self) -> CompanyDataSource:
        return self._source
