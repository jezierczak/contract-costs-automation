from contract_costs.model.company import Company, CompanyType
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.companies.confidence.quality_default import (
    DefaultCompanyQuality,
)

from contract_costs.services.companies.query.dto.company_query import CompanyQuery
from contract_costs.services.companies.query.dto.company_dto import CompanyDTO


class CompanyQueryService:
    def __init__(self, company_repository: CompanyRepository) -> None:
        self._companies = company_repository

    # =====================
    # PUBLIC API
    # =====================
    def list_companies(self, query: CompanyQuery) -> list[CompanyDTO]:
        companies = self._load_companies(query)
        return [self._to_dto(c) for c in companies]

    # =====================
    # LOAD & FILTER
    # =====================
    def _load_companies(self, query: CompanyQuery) -> list[Company]:
        # --- STRICT: tax_number ---
        if query.tax_number:
            company = self._companies.get_by_tax_number(query.tax_number)
            return [company] if company else []

        companies = self._companies.list_all()

        # --- own_only ---
        if query.own_only:
            companies = [
                c for c in companies if c.role == CompanyType.OWN
            ]

        # --- role ---
        if query.role:
            companies = [
                c for c in companies if c.role == query.role
            ]

        # --- active ---
        if not query.include_inactive:
            companies = [
                c for c in companies if c.is_active
            ]

        # --- LIKE search ---
        if query.search:
            phrase = query.search.lower()
            companies = [
                c for c in companies
                if self._matches_search(c, phrase)
            ]

        return companies

    # =====================
    # SEARCH
    # =====================
    @staticmethod
    def _matches_search(company: Company, phrase: str) -> bool:
        haystack = [
            company.name,
            company.description or "",
            company.tax_number,
            company.address.city if company.address else "",
            company.address.street if company.address else "",
            company.contact.email if company.contact else "",
        ]

        return any(
            phrase in (value or "").lower()
            for value in haystack
        )

    # =====================
    # MAPPING
    # =====================
    @staticmethod
    def _to_dto(company: Company) -> CompanyDTO:
        quality = DefaultCompanyQuality.from_company(company)

        return CompanyDTO(
            id=company.id,
            name=company.name,
            tax_number=company.tax_number,
            role=company.role,
            is_active=company.is_active,
            tags=company.tags or set(),
            description=company.description,

            address_street=company.address.street if company.address else None,
            address_city=company.address.city if company.address else None,
            address_zip_code=company.address.zip_code if company.address else None,
            address_country=company.address.country if company.address else None,

            phone_number=company.contact.phone_number if company.contact else None,
            email=company.contact.email if company.contact else None,

            bank_account_number=company.bank_account.number if company.bank_account else None,
            bank_account_country_code=company.bank_account.country_code if company.bank_account else None,
            iban=company.bank_account.iban if company.bank_account else None,

            quality_score=quality.get_overall_score(),
        )
