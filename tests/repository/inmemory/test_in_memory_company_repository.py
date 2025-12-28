from uuid import uuid4

from contract_costs.repository.inmemory.company_repository import (
    InMemoryCompanyRepository
)
from contract_costs.model.company import Company, CompanyType, Address
from contract_costs.services.companies.create_company_service import CreateCompanyService


class TestInMemoryCompanyRepository:

    def test_company_repository_add_and_get(self,contract_owner: Company) -> None:
        repo = InMemoryCompanyRepository()

        repo.add(contract_owner)
        result = repo.get(contract_owner.id)

        assert result is not None
        assert result.id == contract_owner.id
        assert result.name == contract_owner.name

    def test_company_repository_exists(self, contract_owner: Company) -> None:
        repo = InMemoryCompanyRepository()

        assert repo.exists(contract_owner.id) is False

        repo.add(contract_owner)

        assert repo.exists(contract_owner.id) is True

    def test_company_repository_list(
            self,
            contract_owner: Company,
            contract_company: Company,
    ) -> None:
        repo = InMemoryCompanyRepository()

        repo.add(contract_owner)
        repo.add(contract_company)

        companies = repo.list_all()

        assert len(companies) == 2
        assert contract_owner in companies
        assert contract_company in companies

    def test_company_repository_update(self, contract_owner: Company) -> None:
        repo = InMemoryCompanyRepository()

        repo.add(contract_owner)

        updated = Company(
            id=contract_owner.id,
            name="Updated Name",
            description=contract_owner.description,
            tax_number=contract_owner.tax_number,
            address=contract_owner.address,
            contact=contract_owner.contact,
            bank_account=contract_owner.bank_account,
            role=contract_owner.role,
            tags=contract_owner.tags,
            is_active=False,
        )

        repo.update(updated)

        result = repo.get(contract_owner.id)

        assert result is not None
        assert result.name == "Updated Name"
        assert result.is_active is False

    def test_company_repository_get_missing(self) -> None:
        repo = InMemoryCompanyRepository()

        assert repo.get(uuid4()) is None

    def test_system_cannot_start_without_owner(self) -> None:
        repo = InMemoryCompanyRepository()
        assert not repo.exists_owner()

    def test_owner_can_be_added(self) -> None:
        repo = InMemoryCompanyRepository()
        service = CreateCompanyService(repo)

        service.execute(
            name="My Company",
            tax_number="123",
            address=Address(street="str",city="city",zip_code="34-700",country="PL"),
            contact=None,
            role=CompanyType.OWN
        )

        assert repo.exists_owner()
