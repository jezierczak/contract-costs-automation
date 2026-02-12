from contract_costs.model.company import CompanyType
from contract_costs.services.contracts.apply.update_contract_structure_service import UpdateContractStructureService
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.helpers.contract_commands import make_update_structure_command
from tests.helpers.contracts_helpers import make_contract_node, FakeValidator, FakeContractNodeTreeBuilder


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


def test_hard_replace_deletes_and_inserts(
    contract_repo,
    contract_node_repo,
):
    cmd = make_update_structure_command()

    # brak kosztów → HARD
    contract_node_repo._has_values = False

    new_nodes = [make_contract_node(
        organization_id=cmd.organization_id,
        contract_id=cmd.contract_id,
    )]

    builder = FakeContractNodeTreeBuilder(new_nodes)
    validator = FakeValidator()

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

    assert builder.called
    assert validator.called
    assert len(nodes) == 1
