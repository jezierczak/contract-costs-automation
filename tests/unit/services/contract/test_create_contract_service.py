import pytest


from contract_costs.common.ids import new_uuid
from contract_costs.model.contract import ContractType
from contract_costs.model.contract_node import ContractNodeInput
from tests.helpers.contract_commands import make_contract_command

from tests.helpers.contracts_helpers import FakeValidator, FakeContractNodeTreeBuilder, make_contract_node
from contract_costs.services.contracts.create_contract_service import (
    CreateContractService)

def test_create_contract_without_nodes(contract_repo, contract_node_repo, uow):
    builder = FakeContractNodeTreeBuilder(nodes_to_return=[])
    validator = FakeValidator()

    service = CreateContractService(
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    cmd = make_contract_command(contract_node_input=[])

    contract = service.execute(action=cmd, uow=uow)

    contracts = contract_repo.list_contracts(
        organization_id=cmd.organization_id,
        contract_type=ContractType.PROJECT,
    )

    assert len(contracts) == 1
    assert contracts[0].id == contract.id

    nodes = contract_node_repo.list_nodes(
        organization_id=cmd.organization_id
    )

    assert nodes == []
    assert not validator.called
    assert not builder.called


def test_create_contract_with_nodes(contract_repo, contract_node_repo, uow):

    node_input = [{
        "code": "A",
        "name": "Test",
        "budget": None,
        "quantity": None,
        "unit": None,
        "children": [],
        "is_active": True,
    }]

    fake_node = make_contract_node(
        organization_id=None,  # builder nadpisze
        contract_id=None,
    )

    builder = FakeContractNodeTreeBuilder(nodes_to_return=[fake_node])
    validator = FakeValidator()

    service = CreateContractService(
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    cmd = make_contract_command(contract_node_input=node_input)

    contract = service.execute(action=cmd, uow=uow)

    assert builder.called
    assert validator.called

    nodes = contract_node_repo.list_nodes(
        organization_id=cmd.organization_id
    )

    assert len(nodes) == 1
    assert nodes[0].contract_id == contract.id




def test_validator_failure_prevents_persist(
    contract_repo,
    contract_node_repo,
    uow,
):
    node = make_contract_node(
        organization_id=new_uuid(),
        contract_id=new_uuid(),
    )

    builder = FakeContractNodeTreeBuilder(nodes_to_return=[node])
    validator = FakeValidator(should_fail=True)

    service = CreateContractService(
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    node_input: list[ContractNodeInput] = [{
        "code": "X",
        "name": "Test",
        "budget": None,
        "quantity": None,
        "unit": None,
        "children": [],
        "is_active": True,
    }]

    cmd = make_contract_command(node_input)

    with pytest.raises(ValueError):
        service.execute(action=cmd, uow=uow)

    assert contract_repo.list_contracts(cmd.organization_id,contract_type=ContractType.PROJECT) == []
    assert contract_node_repo.list_nodes(organization_id=cmd.organization_id) == []



