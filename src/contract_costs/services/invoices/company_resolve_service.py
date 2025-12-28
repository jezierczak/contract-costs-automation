import re
from uuid import uuid4, UUID
import logging

from contract_costs.infrastructure.openai_invoice_client import OpenAIInvoiceClient
from contract_costs.model.company import Company, Address, BankAccount, CompanyType, Contact
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_tax_number
from contract_costs.services.invoices.dto.parse import CompanyInput

logger = logging.getLogger(__name__)

class CompanyResolveService:

    def __init__(self,
                 company_repo: CompanyRepository,
                 llm_company_resolver: OpenAIInvoiceClient
                 ) -> None:
        self._company_repo = company_repo
        self._llm_company_resolver=llm_company_resolver

    def resolve(self, input_: CompanyInput) -> UUID:

        role = input_.role.strip().upper()
        if role == CompanyType.BUYER.value.upper() or role == CompanyType.OWN.value.upper():

            return self._resolve_buyer(input_)

        else:
            return self._resolve_seller(input_)

        # raise ValueError(f"Unsupported company role: {input_.role}")

    def _resolve_buyer(self, input_: CompanyInput) -> UUID:
        # 1️⃣ Jeśli jest NIP → sprawdzamy, czy to OWNER
        if input_.tax_number:
            tax = normalize_tax_number(input_.tax_number)
            existing = self.find_by_tax_number(tax)
            if existing and existing.role == CompanyType.OWN:
                return existing.id

        # 2️⃣ Fallback LLM – tylko do OWNER-ów
        owners = self._company_repo.get_owners()

        resolved = self._llm_company_resolver.resolve_company(
            input_company=input_,
            companies=owners,
        )

        if resolved and resolved.tax_number:
            tax = normalize_tax_number(resolved.tax_number)
            existing = self.find_by_tax_number(tax)
            if existing and existing.role == CompanyType.OWN:
                return existing.id

        # 3️⃣ Brak jednoznacznego OWNER-a → FAIL
        raise ValueError(
            f"Unable to resolve BUYER as OWNER "
            f"(name={input_.name}, tax={input_.tax_number})"
        )

    def _resolve_seller(self, input_: CompanyInput) -> UUID:
        if not input_.tax_number:
            raise ValueError("SELLER tax number is required")

        tax = normalize_tax_number(input_.tax_number)

        existing = self.find_by_tax_number(tax)
        if existing:
            return existing.id

        # jeśli nie istnieje → tworzymy (świadomie)
        return self._create_seller(input_)

    def _create_seller(self, input_: CompanyInput) -> UUID:
        company = Company(
            id=uuid4(),
            name=input_.name or "UNKNOWN SELLER",
            description=None,
            tax_number=normalize_tax_number(input_.tax_number),
            address=Address(
                street=input_.street or "",
                city=input_.city or "",
                zip_code=input_.zip_code or "",
                country=input_.country or "",
            ),
            contact=Contact(
                phone_number=input_.phone_number,
                email=input_.email,
            ),
            bank_account=(
                BankAccount(input_.bank_account)
                if input_.bank_account else None
            ),
            role=CompanyType.SELLER,
            tags=set(),
            is_active=True,
        )

        self._company_repo.add(company)

        logger.info(
            "Created SELLER from invoice: tax=%s, name=%s",
            company.tax_number,
            company.name,
        )

        return company.id

    # def resolve(self, input_: CompanyInput) -> UUID:
    #     # Szukamy po NIP
    #     if not input_.tax_number:
    #
    #         raise ValueError("Tax number is required")
    #
    #     existing = self.find_by_tax_number(normalize_tax_number(input_.tax_number))
    #     if existing:
    #         return existing.id
    #
    #     # Tworzymy nową firmę
    #     if not input_.name:
    #         logger.warning("UNRECOGNIZED NAME for tax number: %s", input_.tax_number)
    #     company = Company(
    #         id=uuid4(),
    #         name=input_.name or "UNRECOGNIZED NAME",
    #         description=None,
    #         tax_number=normalize_tax_number(input_.tax_number),
    #         address=Address(
    #             street=input_.street or "",
    #             city=input_.city or "",
    #             zip_code=input_.zip_code or "",
    #             country=input_.country or "",
    #         ),
    #         contact=Contact(
    #             phone_number=input_.phone_number,
    #             email=input_.email
    #         ),
    #         bank_account=(
    #             BankAccount(input_.bank_account)
    #             if input_.bank_account else None
    #         ),
    #         role=CompanyType(input_.role),          # ustalisz później
    #         tags=set(),
    #         is_active=True,
    #     )
    #     logger.info(
    #         "Created new company from invoice parse: tax_number=%s, name=%s",
    #         company.tax_number,
    #         company.name,
    #     )
    #     self._company_repo.add(company)
    #     return company.id

    def find_by_tax_number(self, tax_number: str) -> Company | None:
        normalized = normalize_tax_number(tax_number)

        for company in self._company_repo.list_all():
            if normalize_tax_number(company.tax_number) == normalized:
                return company

        return None

    def resolve_seller_or_placeholder(self, tax_number: str) -> Company:
        """
               Resolves seller by tax_number.
               If seller does not exist, creates a placeholder seller:
               - name = 'UNKNOWN SELLER'
               - role = SELLER
               - is_active = False

               Idempotent: one placeholder per tax_number.
               """

        if not tax_number:
            raise ValueError("Seller tax_number is required")

        existing = self._company_repo.get_by_tax_number(tax_number)
        if existing:
            return existing

        logger.warning(
            "Seller not found for tax_number=%s. Creating placeholder seller.",
            tax_number,
        )

        placeholder = Company(
            id=uuid4(),
            name="UNKNOWN SELLER",
            tax_number=tax_number,
            role=CompanyType.SELLER,
            is_active=False,
            description="",
            address=Address(
                street= "",
                city= "",
                zip_code= "",
                country= "",
            ),
            contact=Contact(
                phone_number="",
                email= "",
            ),
            bank_account=(
                None
            ),
            tags=set("placeholder"),
        )

        self._company_repo.add(placeholder)
        return placeholder
