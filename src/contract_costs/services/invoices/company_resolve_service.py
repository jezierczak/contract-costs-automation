import re
from uuid import uuid4, UUID

from contract_costs.model.company import Company, Address, BankAccount, CompanyType
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.invoices.dto.parse import CompanyInput


class CompanyResolveService:

    def __init__(self, company_repo: CompanyRepository) -> None:
        self._company_repo = company_repo

    def resolve(self, input_: CompanyInput) -> UUID:
        # Szukamy po NIP

        existing = self.find_by_tax_number(self._normalize_nip(input_.tax_number))
        if existing:
            return existing.id

        # Tworzymy nową firmę
        company = Company(
            id=uuid4(),
            name=input_.name,
            description=None,
            tax_number=self._normalize_nip(input_.tax_number),
            address=Address(
                street=input_.street or "",
                city=input_.city or "",
                zip_code=input_.zip_code or "",
                country=input_.country or "",
            ),
            bank_account=(
                BankAccount(input_.bank_account)
                if input_.bank_account else None
            ),
            role=CompanyType(input_.role),          # ustalisz później
            tags=set(),
            is_active=True,
        )

        self._company_repo.add(company)
        return company.id

    def find_by_tax_number(self, tax_number: str) -> Company | None:
        for company in self._company_repo.list():
            if company.tax_number == self._normalize_nip(tax_number):
                return company
        return None

    @staticmethod
    def _normalize_nip(nip: str | int) -> str:
        if isinstance(nip, int):
            nip = str(nip)
        return re.sub(r'^\s*PL\s*', '', nip, flags=re.IGNORECASE)

