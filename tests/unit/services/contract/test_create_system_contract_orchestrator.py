from uuid import uuid4
from unittest.mock import MagicMock

from contract_costs.model.contract import ContractStatus, ContractType
from contract_costs.services.contracts.dto.create_contract_command import CreateContractCommand
from contract_costs.services.contracts.system_contract.create_system_contract_orchestrator import (
    CreateSystemContractOrchestrator,
)
from tests.builders.company_builder import CompanyBuilder


class _FakeUow:
    def __init__(self, contract_repo):
        self.contracts = contract_repo


def test_execute_is_idempotent_when_system_contract_exists():
    owner = CompanyBuilder().build()
    existing_contract = MagicMock()

    contract_repo = MagicMock()
    contract_repo.get_system_contract.return_value = existing_contract

    create_contract_service = MagicMock()

    service = CreateSystemContractOrchestrator(
        create_contract_service=create_contract_service,
    )

    uow = _FakeUow(contract_repo)
    service.execute(
        uow=uow,
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        owner=owner,
    )

    create_contract_service.execute.assert_not_called()


def test_execute_creates_system_contract_when_missing():
    organization_id = uuid4()
    actor_user_id = uuid4()
    owner = CompanyBuilder().with_tax_number("1234567890").with_name("ACME").build()

    contract_repo = MagicMock()
    contract_repo.get_system_contract.return_value = None

    create_contract_service = MagicMock()

    service = CreateSystemContractOrchestrator(
        create_contract_service=create_contract_service,
    )

    uow = _FakeUow(contract_repo)
    service.execute(
        uow=uow,
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        owner=owner,
    )

    contract_repo.get_system_contract.assert_called_once_with(
        organization_id=organization_id,
        owner_id=owner.id,
    )
    create_contract_service.execute.assert_called_once()

    command = create_contract_service.execute.call_args.kwargs["action"]
    assert isinstance(command, CreateContractCommand)
    assert command.organization_id == organization_id
    assert command.actor_user_id == actor_user_id
    assert command.owner == owner
    assert command.client is None
    assert command.code == "SYSTEM_1234567890"
    assert command.contract_type == ContractType.SYSTEM
    assert command.status == ContractStatus.ACTIVE

    assert command.contract_node_input is not None
    assert len(command.contract_node_input) == 1
    root = command.contract_node_input[0]
    assert root["code"] == "ROOT"

    children = root["children"]
    assert len(children) == 7
    child_codes = {child["code"] for child in children}
    assert child_codes == {"ADMIN", "FIN", "UTIL", "TAX", "ZUS", "BOOK", "OTHER"}
    assert create_contract_service.execute.call_args.kwargs["uow"] is uow
