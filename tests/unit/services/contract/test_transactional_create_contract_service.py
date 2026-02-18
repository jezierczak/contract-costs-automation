import pytest

from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.helpers.contract_commands import make_contract_command
from tests.helpers.contracts_helpers import FakeContractNodeTreeBuilder, FakeValidator


def test_create_contract_with_uow_persists_contract():
    uow = InMemoryUnitOfWork()
    service = CreateContractService(
        contract_node_tree_builder=FakeContractNodeTreeBuilder(nodes_to_return=[]),
        contract_node_tree_validator=FakeValidator(),
    )

    cmd = make_contract_command(contract_node_input=[])
    contract = service.execute(action=cmd, uow=uow)

    persisted = uow.contracts.get(organization_id=cmd.organization_id, contract_id=contract.id)
    assert persisted is not None


def test_create_contract_propagates_validator_error():
    uow = InMemoryUnitOfWork()
    service = CreateContractService(
        contract_node_tree_builder=FakeContractNodeTreeBuilder(nodes_to_return=[]),
        contract_node_tree_validator=FakeValidator(should_fail=True),
    )

    cmd = make_contract_command(contract_node_input=[{"code": "A", "name": "A", "budget": None, "quantity": None, "unit": None, "children": [], "is_active": True}])

    with pytest.raises(ValueError, match="Invalid tree"):
        service.execute(action=cmd, uow=uow)
