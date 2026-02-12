from dataclasses import replace
from datetime import datetime
from uuid import uuid4, UUID

from contract_costs.repository.inmemory.company_repository import (
    InMemoryCompanyRepository
)
from contract_costs.model.company import Company, CompanyType, Address
from contract_costs.services.companies.create_company_service import CreateCompanyService
from contract_costs.services.companies.dto.create_company_command import CreateCompanyCommand

TEST_ORG_ID = uuid4()
TEST_USER_ID = uuid4()
NOW = datetime.now()


def make_company(
        *,
        company_id: UUID | None = None,
        name: str = "Test Company",
        tax_number: str = "1234567890",
        role: CompanyType = CompanyType.CLIENT,
        is_active: bool = True,
        organization_id: UUID = TEST_ORG_ID,
) -> Company:
    return Company(
        id=company_id or uuid4(),
        organization_id=organization_id,

        name=name,
        description=None,
        tax_number=tax_number,

        address=Address("Street", "City", "00-000", "PL"),
        contact=None,
        bank_account=None,

        role=role,
        tags=set(),
        is_active=is_active,

        created_at=NOW,
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

class TestInMemoryCompanyRepository:



    def test_company_repository_add_and_get(self) -> None:
        repo = InMemoryCompanyRepository()
        company = make_company()

        repo.add(company)
        result = repo.get(company.id, company.organization_id)

        assert result is not None
        assert result.id == company.id
        assert result.name == company.name

    def test_company_repository_exists(self) -> None:
        repo = InMemoryCompanyRepository()
        company = make_company()

        assert repo.exists(company.id, company.organization_id) is False

        repo.add(company)

        assert repo.exists(company.id, company.organization_id) is True

    def test_company_repository_list(self) -> None:
        repo = InMemoryCompanyRepository()

        owner = make_company(role=CompanyType.OWN)
        other = make_company(role=CompanyType.CLIENT)

        repo.add(owner)
        repo.add(other)

        companies = repo.list_all(owner.organization_id)

        assert len(companies) == 2
        assert owner in companies
        assert other in companies

    def test_company_repository_update(self) -> None:
        repo = InMemoryCompanyRepository()
        company = make_company()

        repo.add(company)

        updated = replace(
            company,
            name="Updated Name",
            is_active=False,
            updated_at=NOW,
            updated_by_user_id=TEST_USER_ID,
        )

        repo.update(updated)

        result = repo.get(company.id,TEST_ORG_ID)

        assert result is not None
        assert result.name == "Updated Name"
        assert result.is_active is False
        assert result.updated_at == NOW
        assert result.updated_by_user_id == TEST_USER_ID

    def test_company_repository_get_missing(self) -> None:
        repo = InMemoryCompanyRepository()

        assert repo.get(uuid4(), TEST_ORG_ID) is None

    def test_system_cannot_start_without_owner(self) -> None:
        repo = InMemoryCompanyRepository()

        assert not repo.exists_owner(TEST_ORG_ID)

    def test_owner_can_be_added(self) -> None:
        repo = InMemoryCompanyRepository()
        service = CreateCompanyService(repo)

        cmd = CreateCompanyCommand(
            organization_id=TEST_ORG_ID,
            actor_user_id=TEST_USER_ID,

            name="My Company",
            tax_number="1234567890",
            role=CompanyType.OWN,

            address=Address("str", "city", "34-700", "PL"),
            contact=None,
            bank_account=None,
            tags=None,
        )

        service.execute(cmd)

        assert repo.exists_owner(TEST_ORG_ID)

