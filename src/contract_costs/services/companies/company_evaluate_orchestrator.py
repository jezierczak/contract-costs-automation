import logging
from dataclasses import replace
from datetime import datetime
from enum import Enum
from typing import Callable
from uuid import uuid4, UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.infrastructure.openai_invoice_client import OpenAIInvoiceClient
from contract_costs.model.company import Company, CompanyType, BankAccount, Contact, Address, \
    CompanyVerificationStatus

from contract_costs.services.companies.confidence.fields import CompanyField
from contract_costs.services.companies.confidence.quality_default import DefaultCompanyQuality
from contract_costs.services.companies.normalize.normalize_service import CompanyNormalizeService

from contract_costs.services.companies.providers.candidate_provider import CompanyCandidateProvider
from contract_costs.services.companies.providers.excact_nip import ExactNipCandidateProvider
from contract_costs.services.companies.validators.company import CompanyValidator
from contract_costs.services.financial_records.assigment.invoice_sources.pdf.parsers.dto.parse import CompanyInput
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

class EvaluateMode(Enum):
    NO_CREATE = 0
    NORMAL = 1
    AUTHORITATIVE = 2

class CompanyEvaluateOrchestrator:

    def __init__(
        self,
        suggestion_provider: CompanyCandidateProvider,
        llm_company_resolver: OpenAIInvoiceClient,
        clock: Callable[[], datetime] = utc_now,

    ) -> None:
        self._llm_company_resolver = llm_company_resolver
        self._exact_provider = ExactNipCandidateProvider()
        self._suggestion_provider = suggestion_provider
        self._normalizator = CompanyNormalizeService()
        self._clock = clock

    def evaluate_from_tax(   self,
                    *,
                    uow: UnitOfWork,
                    organization_id: UUID,
                    actor_user_id: UUID,
                    input_tax_number: str | None,
                    role: CompanyType,mode: EvaluateMode = EvaluateMode.NORMAL
                ) -> Company:

        if not input_tax_number:
            raise ValueError("No tax number provided, unable to evaluate company")
        return self.evaluate(
            uow=uow,
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            input_= CompanyInput(
                name=None,
                tax_number=str(input_tax_number),
                state=None,
                street=None,
                zip_code=None,
                city=None,
                phone_number=None,
                email=None,
                country=None,
                bank_account=None,
                role=role.value,
            ),
            mode=mode
        )

    def evaluate(
            self,
            *,
            uow:UnitOfWork,
            organization_id: UUID,
            actor_user_id: UUID,
            input_: CompanyInput,
            mode: EvaluateMode = EvaluateMode.NORMAL,
    ) -> Company:
        """
        Main entry point for company resolution.

        Rules:
        1. Match ONLY by exact tax number (or raw TMP-/AI- placeholder)
        2. No match → CREATE (unless NO_CREATE)
        3. Match → fill in data (see _maybe_update); tax number never changes

        Fuzzy providers (name, bank, email, ...) never decide - see suggest().
        """

        candidates = self._exact_provider.find_candidates(uow=uow, organization_id=organization_id, input_=input_)
        logger.info("Evaluating company %s (tax=%s)", input_.name, input_.tax_number)

        if not candidates:
            if mode == EvaluateMode.NO_CREATE:
                raise RuntimeError(f"({mode.value} mode) No candidates found for NIP: {input_.tax_number}")
            logger.info("No company with this tax number → creating new company")
            return self._create_company(
                uow=uow,
                organization_id=organization_id,
                actor_user_id=actor_user_id,
                input_=input_)

        return self._maybe_update(
            uow=uow,
            organization_id= organization_id,
            actor_user_id= actor_user_id,
            company=candidates[0],
            input_=input_,
            mode=mode)

    def suggest(
            self,
            *,
            uow: UnitOfWork,
            organization_id: UUID,
            input_: CompanyInput,
    ) -> list[Company]:
        """
        Fuzzy candidates (name, bank account, email, street, phone) as hints
        for the user - never used to pick a company automatically.
        """
        return self._suggestion_provider.find_candidates(
            uow=uow,
            organization_id=organization_id,
            input_=input_,
        )

    # ---- hooks / extension points ----

    def _create_company( self,
                        *,
                        uow:UnitOfWork,
                        organization_id: UUID,
                        actor_user_id: UUID,
                        input_: CompanyInput,
                        id_generator: Callable[[], UUID] = new_uuid
                        ) -> Company:
        normalized_tax = self._normalizator.normalize_tax_number(input_.tax_number)
        tax_number = (
            normalized_tax
            if normalized_tax is not None
            else self.generate_placeholder_tax_number()
        )

        company = Company(
            id=id_generator(),
            organization_id=organization_id,

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
            # pewny NIP + nazwa z dokumentu = firma gotowa; inaczej użytkownik ją uzupełnia
            verification_status=(
                CompanyVerificationStatus.VERIFIED
                if normalized_tax is not None
                and CompanyValidator.is_trusted_tax_number(normalized_tax)
                and (input_.name or "").strip()
                else CompanyVerificationStatus.TO_VERIFY
            ),

            created_at=self._clock(),
            created_by_user_id=actor_user_id,

            updated_at=None,
            updated_by_user_id=None,
        )

        uow.companies.add(company)

        logger.info(
            "Created SELLER from invoice: tax=%s, name=%s",
            company.tax_number,
            company.name,
        )

        return company

    def _update_company_field(
            self,
            *,
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
            n_value = self._normalizator.normalize_email(value)
            if not n_value:
                return company
            contact = company.contact or Contact(phone_number=None, email=None)
            return replace(company, contact=replace(contact, email=n_value))

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

    def _maybe_update(self,
                            *,
                            uow: UnitOfWork,
                            organization_id: UUID,
                            actor_user_id: UUID,
                            company: Company,
                            input_: CompanyInput,
                            mode: EvaluateMode) -> Company:
        """
        Updates matched company with incoming data.

        Rules:
        - tax number is NEVER changed (it is the match key)
        - AUTHORITATIVE (e.g. seller from KSeF) overwrites every other field present in input
        - otherwise only empty fields are filled in
        """

        input_quality = DefaultCompanyQuality.from_input(input_)
        company_quality = DefaultCompanyQuality.from_company(company)
        authoritative = mode == EvaluateMode.AUTHORITATIVE

        updated_company = company

        for field in CompanyField:
            if field == CompanyField.TAX_NUMBER:
                continue
            if not input_quality.has_field(field):
                continue
            if company_quality.has_field(field) and not authoritative:
                continue

            candidate = self._update_company_field(
                company=updated_company,
                field=field,
                value=input_quality.get_value(field),
            )
            if candidate != updated_company:
                logger.info(
                    "Updated field %s for company %s (authoritative=%s)",
                    field.value,
                    company.name,
                    authoritative,
                )
            updated_company = candidate

        if updated_company == company:
            return company

        updated_company = replace(
            updated_company,
            updated_at=self._clock(),
            updated_by_user_id=actor_user_id,
        )
        uow.companies.update(updated_company)
        return updated_company


    @staticmethod
    def generate_placeholder_tax_number() -> str:
        return f"TMP-{uuid4().hex[:8]}"


