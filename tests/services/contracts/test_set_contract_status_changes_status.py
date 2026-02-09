from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest

from contract_costs.common.time import utc_now
from contract_costs.model.company import CompanyType, Company, Address, Contact
from contract_costs.model.contract import ContractStatus, Contract
from contract_costs.repository.inmemory.contract_repository import InMemoryContractRepository
from contract_costs.services.contracts.apply.command.set_contract_status_command import SetContractStatusCommand
from contract_costs.services.contracts.apply.set_contract_status_service import SetContractStatusService


TEST_ORG_ID = uuid4()
TEST_USER_ID = uuid4()


def make_company(
    *,
    name: str = "Test Company",
    tax_number: str = "1234567890",
    role: CompanyType = CompanyType.OWN,
) -> Company:
    return Company(
        id=uuid4(),
        organization_id=TEST_ORG_ID,

        name=name,
        description=None,
        tax_number=tax_number,
        address=Address(
            street="Test Street",
            city="Test City",
            zip_code="00-000",
            country="PL",
        ),
        contact=Contact(
            phone_number=None,
            email=None,
        ),
        bank_account=None,
        role=role,
        tags=set(),
        is_active=True,

        created_at=utc_now(),
        created_by_user_id=TEST_USER_ID,
        updated_at=None,
        updated_by_user_id=None,
    )

def make_contract(
    *,
    status: ContractStatus = ContractStatus.PLANNED,
    code: str = "TEST",
    name: str = "Test Contract",
) -> Contract:
    owner = make_company(
        name="Owner Company",
        tax_number="1111111111",
    )
    return Contract(
        id=uuid4(),
        code=code,
        name=name,
        description=None,
        owner=owner,          # jeśli wymagane → możesz dodać fake Company
        client=None,
        start_date=date.today(),
        end_date=None,
        budget=None,
        path=Path("test/path"),
        status=status,
    )

@pytest.fixture
def repo():
    return InMemoryContractRepository()

@pytest.fixture
def service(repo: InMemoryContractRepository):
    return SetContractStatusService(repo)

def test_set_contract_status_changes_status(repo: InMemoryContractRepository,service: SetContractStatusService):

    contract = make_contract(status=ContractStatus.PLANNED)
    repo.add(contract)

    cmd = SetContractStatusCommand(
        contract_id=contract.id,
        new_status=ContractStatus.ACTIVE,
    )

    service.execute(cmd)

    updated = repo.get(contract.id)
    assert updated.status == ContractStatus.ACTIVE


def test_set_contract_status_idempotent(repo: InMemoryContractRepository,service: SetContractStatusService):

    contract = make_contract(status=ContractStatus.ACTIVE)
    repo.add(contract)

    cmd = SetContractStatusCommand(
        contract_id=contract.id,
        new_status=ContractStatus.ACTIVE,
    )

    service.execute(cmd)

    updated = repo.get(contract.id)
    assert updated.status == ContractStatus.ACTIVE
