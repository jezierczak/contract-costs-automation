import logging
from dataclasses import replace
from uuid import uuid4

from contract_costs.infrastructure.openai_invoice_client import OpenAIInvoiceClient
from contract_costs.model.company import Company, CompanyType, BankAccount, Contact, Address
from contract_costs.repository.company_repository import CompanyRepository

from contract_costs.services.companies.confidence.fields import CompanyField
from contract_costs.services.companies.confidence.quality_default import DefaultCompanyQuality
from contract_costs.services.companies.normalize.normalize_service import CompanyNormalizeService

from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.invoices.dto.parse import CompanyInput

logger = logging.getLogger(__name__)

FULL_UPDATE_THRESHOLD = 85

class CompanyEvaluateOrchestrator:

    def __init__(
        self,
        company_repo: CompanyRepository,
        candidate_provider: CompanyCandidateProvider,
        llm_company_resolver: OpenAIInvoiceClient

    ) -> None:
        self._llm_company_resolver = llm_company_resolver
        self._company_repo = company_repo
        self._candidate_provider = candidate_provider
        self._normalizator = CompanyNormalizeService()

    def evaluate_from_tax(self, input_tax_number: str | None, role: CompanyType) -> Company:
        if not input_tax_number:
            raise ValueError("No tax number provided, unable to evaluate company")
        return self.evaluate(
            CompanyInput(
                name=None,
                tax_number=input_tax_number,
                state=None,
                street=None,
                zip_code=None,
                city=None,
                phone_number=None,
                email=None,
                country=None,
                bank_account=None,
                role=role.value,
            )
        )

    def evaluate(self, input_: CompanyInput) -> Company:
        """
        Main entry point for company resolution.

        Rules:
        1. If no candidates → CREATE
        2. If candidates exist → NEVER create
        3. Select best candidate by quality
        4. Update best candidate with better incoming data
        """

        candidates = self._candidate_provider.find_candidates(input_)
        logger.info(f"Evaluating company {input_.name}")

        for candidate in candidates:
            logger.info(f"Candidate: {candidate.name}")

        if not candidates:
            logger.info("No candidates found → creating new company")
            return self._create_company(input_)

            # 🔹 2️⃣ Preferuj OWN (jeśli są)
        own_candidates = [
            c for c in candidates
            if c.role == CompanyType.OWN and c.is_active
        ]

        pool = own_candidates if own_candidates else candidates

        best = max(
            pool,
            key=lambda c: DefaultCompanyQuality.from_company(c).get_overall_score()
        )

        return self._maybe_update(best, input_)

    # ---- hooks / extension points ----

    def _create_company(self, input_: CompanyInput) -> Company:
        normalized_tax = self._normalizator.normalize_tax_number(input_.tax_number)
        tax_number = (
            normalized_tax
            if normalized_tax is not None
            else self.generate_placeholder_tax_number()
        )

        company = Company(
            id=uuid4(),
            name=input_.name or "UNKNOWN SELLER",
            description=None,
            tax_number=tax_number,
            address=Address(
                street=input_.street or "",
                city=input_.city or "",
                zip_code=input_.zip_code or "",
                country=input_.country or "",
            ),
            contact=Contact(
                phone_number=self._normalizator.normalize_phone(input_.phone_number),
                email=self._normalizator.normalize_email(input_.email),
            ),
            bank_account=(
                BankAccount(self._normalizator.normalize_bank_account(input_.bank_account))
                if input_.bank_account else None
            ),
            role=CompanyType(input_.role),
            tags=set(),
            is_active=True,
        )

        self._company_repo.add(company)

        logger.info(
            "Created SELLER from invoice: tax=%s, name=%s",
            company.tax_number,
            company.name,
        )

        return company

    def _update_company_field(
            self,
            company: Company,
            field: CompanyField,
            value: str | None,
    ) -> Company:

        logger.info(
            "Updating company field: field=%s, updated_data=%s",
            field.value,
            value,
        )

        if field == CompanyField.TAX_NUMBER:
            normalized = self._normalizator.normalize_tax_number(value)
            if normalized is None:
                return company
            return replace(company, tax_number=normalized)

        if field == CompanyField.NAME:
            if value is not None:
                return replace(company, name=value)

        if field == CompanyField.EMAIL:
            contact = company.contact or Contact(phone_number=None, email=None)
            return replace(company, contact=replace(contact, email=self._normalizator.normalize_email(value)))

        if field == CompanyField.PHONE_NUMBER:
            n_value = self._normalizator.normalize_phone(value)
            if not n_value:
                return company
            contact = company.contact or Contact(phone_number=None, email=None)
            return replace(company, contact=replace(contact, phone_number=n_value))

        if field == CompanyField.STREET:
            address = company.address or Address("", "", "", "")
            return replace(company, address=replace(address, street=value))

        if field == CompanyField.CITY:
            address = company.address or Address("", "", "", "")
            return replace(company, address=replace(address, city=value))

        if field == CompanyField.ZIP_CODE:
            address = company.address or Address("", "", "", "")
            return replace(company, address=replace(address, zip_code=value))

        if field == CompanyField.COUNTRY:
            address = company.address or Address("", "", "", "")
            return replace(company, address=replace(address, country=value))

        if field == CompanyField.BANK_ACCOUNT:
            normalized = self._normalizator.normalize_bank_account(value)
            if not normalized:
                return company
            return replace(company, bank_account=BankAccount(normalized))

        return company

    def _maybe_update(self, company: Company, input_: CompanyInput) -> Company:
        """
        Updates company data based on input quality.

        Rules:
        - FULL UPDATE if input_overall_score >= FULL_UPDATE_THRESHOLD
        - SOFT UPDATE otherwise
        - Field is updated ONLY if input_field_score > company_field_score
        """

        input_quality = DefaultCompanyQuality.from_input(input_)
        company_quality = DefaultCompanyQuality.from_company(company)

        input_overall = input_quality.get_overall_score()
        company_overall = company_quality.get_overall_score()

        full_update = input_overall >= FULL_UPDATE_THRESHOLD and input_overall>company_overall

        logger.info(
            "Company update decision: full_update=%s input_score=%s company_score=%s company=%s",
            full_update,
            input_overall,
            company_overall,
            company.name,
        )

        updated_company = company
        changed = False

        for field in CompanyField:

            if not input_quality.has_field(field):
                continue

            input_score = input_quality.get_field_score(field)
            company_score = company_quality.get_field_score(field)

            # 🔴 SOFT UPDATE
            if not full_update:
                if input_score <= company_score:
                    continue

            # 🔥 FULL UPDATE
            else:
                if input_score <= 0:
                    continue

            input_value = input_quality.get_value(field)
            company_value = company_quality.get_value(field)

            if input_value == company_value:
                continue

            # 🔥 aktualizacja
            updated_company = self._update_company_field(
                updated_company,
                field,
                input_value,
            )
            changed = True

            logger.info(
                "Updated field %s for company %s (input_score=%s company_score=%s)",
                field.value,
                company.name,
                input_score,
                company_score,
            )

        if changed:
            self._company_repo.update(updated_company)
            return updated_company

        return company


    @staticmethod
    def generate_placeholder_tax_number() -> str:
        return f"TMP-{uuid4().hex[:8]}"


