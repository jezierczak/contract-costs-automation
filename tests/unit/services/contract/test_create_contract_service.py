import pytest


from contract_costs.common.ids import new_uuid
from tests.helpers.contract_commands import make_contract_command

from tests.helpers.contracts_helpers import FakeValidator, FakeContractNodeTreeBuilder, make_contract_node
from contract_costs.services.contracts.create_contract_service import (
    CreateContractService)

def test_create_contract_without_nodes(contract_repo, contract_node_repo):
    builder = FakeContractNodeTreeBuilder(nodes_to_return=[])
    validator = FakeValidator()

    service = CreateContractService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    cmd = make_contract_command()

    service.init(cmd)
    service.execute()

    assert contract_repo.list_contracts(cmd.organization_id)
    assert contract_node_repo.list_nodes(organization_id=cmd.organization_id) == []
    assert not validator.called

def test_create_contract_with_nodes(contract_repo, contract_node_repo):

    builder = FakeContractNodeTreeBuilder(nodes_to_return=[])
    validator = FakeValidator()

    service = CreateContractService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )
    cmd = make_contract_command()
    service.init(cmd)

    contract_id = service._contract.id

    node = make_contract_node(
        organization_id=cmd.organization_id,
        contract_id=contract_id,
    )

    builder.nodes_to_return = [node]

    service.add_contract_node_tree([])
    service.execute()

    assert validator.called
    assert builder.called

    nodes = contract_node_repo.list_nodes(
        organization_id=cmd.organization_id
    )

    assert len(nodes) == 1
    saved = contract_repo.list_contracts(cmd.organization_id)[0]
    assert saved.code == cmd.code
    assert saved.name == cmd.name


def test_validator_failure_prevents_persist(
    contract_repo,
    contract_node_repo,
):
    node = make_contract_node(
        organization_id=new_uuid(),
        contract_id=new_uuid(),
    )

    builder = FakeContractNodeTreeBuilder(nodes_to_return=[node])
    validator = FakeValidator(should_fail=True)

    service = CreateContractService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    cmd = make_contract_command()

    service.init(cmd)
    service.add_contract_node_tree([])

    with pytest.raises(ValueError):
        service.execute()

    assert contract_repo.list_contracts(cmd.organization_id) == []
    assert contract_node_repo.list_nodes(organization_id=cmd.organization_id) == []


def test_add_nodes_without_init_raises(
    contract_repo,
    contract_node_repo,
):
    builder = FakeContractNodeTreeBuilder([])
    validator = FakeValidator()

    service = CreateContractService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    with pytest.raises(RuntimeError):
        service.add_contract_node_tree([])


def test_execute_without_init_raises(
    contract_repo,
    contract_node_repo,
):
    builder = FakeContractNodeTreeBuilder([])
    validator = FakeValidator()

    service = CreateContractService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    with pytest.raises(RuntimeError):
        service.execute()
