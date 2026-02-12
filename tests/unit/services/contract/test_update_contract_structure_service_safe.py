from dataclasses import replace

import pytest
from decimal import Decimal

from contract_costs.model.company import CompanyType
from contract_costs.services.contracts.apply.update_contract_structure_service import UpdateContractStructureService
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.helpers.contract_commands import make_update_structure_command

from tests.helpers.contracts_helpers import FakeValidator, FakeContractNodeTreeBuilder
from tests.unit.services.contract.test_create_contract_service import (
    make_contract_node,
)




# class FakeBuilder(ContractNodeTreeBuilder):
#     def __init__(self, nodes):
#         self.nodes = nodes
#         self.called = False
#
#     def build(self, **kwargs):
#         self.called = True
#         return self.nodes
#
#
# class FakeValidator(ContractNodeEntityValidator):
#     def __init__(self, should_fail=False):
#         self.called = False
#         self.should_fail = should_fail
#
#     def validate(self, nodes):
#         self.called = True
#         if self.should_fail:
#             raise ValueError("Invalid tree")


def test_safe_replace_updates_inserts_deletes(
    contract_repo,
    contract_node_repo,
):
    cmd = make_update_structure_command()

    # --- istniejące nody ---
    node_a = make_contract_node(
        organization_id=cmd.organization_id,
        contract_id=cmd.contract_id,
        code="A",
    )

    node_b = make_contract_node(
        organization_id=cmd.organization_id,
        contract_id=cmd.contract_id,
        code="B",
    )

    contract_node_repo.add_all([node_a, node_b])

    # --- nowe nody z Excela ---
    updated_a = replace(
        node_a,
        budget=Decimal("200"),
    )

    new_c = make_contract_node(
        organization_id=cmd.organization_id,
        contract_id=cmd.contract_id,
        code="C",
    )

    builder = FakeContractNodeTreeBuilder([updated_a, new_c])
    validator = FakeValidator()

    # 🔥 SAFE mode
    contract_node_repo.has_values = lambda **kwargs: True
    contract_node_repo.node_has_values = lambda **kwargs: False

    service = UpdateContractStructureService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )
    contract = (ContractBuilder()
                .with_organization_id(cmd.organization_id)
                .with_id(cmd.contract_id)
                .with_owner(CompanyBuilder().with_role(CompanyType.OWN).build())
                .with_status(cmd.status)
                .build())

    contract_repo.add(contract)

    service.execute(cmd)

    nodes = contract_node_repo.list_by_contract(
        contract_id=cmd.contract_id,
        organization_id=cmd.organization_id,
    )

    codes = {n.code for n in nodes}

    assert builder.called
    assert validator.called
    assert codes == {"A", "C"}


def test_safe_replace_blocks_delete_if_node_has_values(
    contract_repo,
    contract_node_repo,
):
    cmd = make_update_structure_command()

    node_a = make_contract_node(
        organization_id=cmd.organization_id,
        contract_id=cmd.contract_id,
        code="A",
    )

    contract_node_repo.add_all([node_a])

    # Excel NIE zawiera A → próba delete
    builder = FakeContractNodeTreeBuilder([])

    validator = FakeValidator()

    contract_node_repo.has_values = lambda **kwargs: True
    contract_node_repo.node_has_values = lambda **kwargs: True  # 🔥 blokada

    service = UpdateContractStructureService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    with pytest.raises(ValueError):
        service.execute(cmd)


def test_safe_replace_only_updates_existing(
    contract_repo,
    contract_node_repo,
):
    cmd = make_update_structure_command()

    node_a = make_contract_node(
        organization_id=cmd.organization_id,
        contract_id=cmd.contract_id,
        code="A",
    )

    contract_node_repo.add_all([node_a])

    updated_a = replace(
        node_a,
        budget=Decimal("999"),
    )

    builder = FakeContractNodeTreeBuilder([updated_a])
    validator = FakeValidator()

    contract_node_repo.has_values = lambda **kwargs: True
    contract_node_repo.node_has_values = lambda **kwargs: False

    service = UpdateContractStructureService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )
    contract = (ContractBuilder()
                .with_organization_id(cmd.organization_id)
                .with_id(cmd.contract_id)
                .with_owner(CompanyBuilder().with_role(CompanyType.OWN).build())
                .with_status(cmd.status)
                .build())

    contract_repo.add(contract)
    service.execute(cmd)

    nodes = contract_node_repo.list_by_contract(
        contract_id=cmd.contract_id,
        organization_id=cmd.organization_id,
    )

    assert len(nodes) == 1
    assert nodes[0].budget == Decimal("999")


def test_safe_replace_only_inserts_when_no_existing_nodes(
    contract_repo,
    contract_node_repo,
):
    cmd = make_update_structure_command()

    new_node = make_contract_node(
        organization_id=cmd.organization_id,
        contract_id=cmd.contract_id,
        code="X",
    )

    builder = FakeContractNodeTreeBuilder([new_node])
    validator = FakeValidator()

    contract_node_repo.has_values = lambda **kwargs: True
    contract_node_repo.node_has_values = lambda **kwargs: False

    service = UpdateContractStructureService(
        contract_repository=contract_repo,
        contract_node_repository=contract_node_repo,
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    contract =(ContractBuilder()
               .with_organization_id(cmd.organization_id)
                .with_id(cmd.contract_id)
                .with_owner(CompanyBuilder().with_role(CompanyType.OWN).build())
                .with_status(cmd.status)
               .build())


    contract_repo.add(contract)

    service.execute(cmd)

    nodes = contract_node_repo.list_by_contract(
        contract_id=cmd.contract_id,
        organization_id=cmd.organization_id,
    )

    assert len(nodes) == 1
    assert nodes[0].code == "X"
