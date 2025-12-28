from uuid import uuid4

from contract_costs.model.company import Company, CompanyType, Address, BankAccount, Contact
from contract_costs.repository.company_repository import CompanyRepository
from contract_costs.services.common.resolve_utils import normalize_required_tax_number


class CreateCompanyService:

    def __init__(self, company_repository: CompanyRepository) -> None:
        self._companies = company_repository

    def execute(
        self,
        *,
        name: str,
        tax_number: str,
        address: Address | None = None,
        contact: Contact | None = None,
        role: CompanyType,
        description: str | None = None,
        bank_account: BankAccount | None = None,
        tags: set[str] | None = None,
    ) -> Company:
        normalized = normalize_required_tax_number(tax_number)

        if self._companies.get_by_tax_number(normalized):
            raise ValueError("Company with this tax number already exists")

        company = Company(
            id=uuid4(),
            name=name,
            description=description,
            tax_number=normalized,
            address=address if address else Address(
                street="",
                city="",
                country="",
                zip_code="",
            ),
            contact=contact if contact else Contact(
                phone_number="",
                email="",
            ),
            bank_account=bank_account,
            role=role,
            tags=tags or set(),
            is_active=True,
        )

        self._companies.add(company)
        return company
