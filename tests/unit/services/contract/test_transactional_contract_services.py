from datetime import datetime
from uuid import uuid4

import pytest

from contract_costs.model.company import CompanyType
from contract_costs.services.contracts.apply.update_contract_structure_service import UpdateContractStructureService
from contract_costs.services.contracts.migration.back_fill_system_contracts_service import BackfillSystemContractsService
from contract_costs.services.contracts.migration.backfill_system_contracts_command import BackfillSystemContractsCommand
from contract_costs.services.contracts.system_contract.create_system_contract_orchestrator import CreateSystemContractOrchestrator
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.helpers.contract_commands import make_update_structure_command
from tests.helpers.contracts_helpers import FakeContractNodeTreeBuilder, FakeValidator


class _FakeCreateContractService:
    def __init__(self):
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)


class _FakeCreateSystemContract:
    def __init__(self):
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)


def test_update_structure_uses_uow_and_updates_contract():
    uow = InMemoryUnitOfWork()
    contract = ContractBuilder().build()
    uow.contracts.add(contract)

    service = UpdateContractStructureService(
        contract_node_tree_builder=FakeContractNodeTreeBuilder(nodes_to_return=[]),
        contract_node_tree_validator=FakeValidator(),
        clock=lambda: datetime(2026, 2, 16, 12, 0, 0),
    )

    cmd = make_update_structure_command(
        organization_id=contract.organization_id,
        actor_user_id=uuid4(),
        contract_id=contract.id,
        contract_node_input=[],
    )

    service.execute(action=cmd, uow=uow)

    updated = uow.contracts.get(organization_id=contract.organization_id, contract_id=contract.id)
    assert updated is not None
    assert updated.name == cmd.name


def test_update_structure_raises_for_missing_contract():
    service = UpdateContractStructureService(
        contract_node_tree_builder=FakeContractNodeTreeBuilder(nodes_to_return=[]),
        contract_node_tree_validator=FakeValidator(),
    )

    with pytest.raises(ValueError, match="does not exist"):
        service.execute(action=make_update_structure_command(contract_node_input=[]), uow=InMemoryUnitOfWork())


def test_create_system_contract_passes_uow_to_create_contract_service():
    uow = InMemoryUnitOfWork()
    fake_create = _FakeCreateContractService()

    orchestrator = CreateSystemContractOrchestrator(create_contract_service=fake_create)
    orchestrator.execute(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        owner=CompanyBuilder().build(),
        uow=uow,
    )

    assert len(fake_create.calls) == 1
    assert fake_create.calls[0]["uow"] is uow


def test_backfill_calls_orchestrator_for_each_owner_from_uow():
    uow = InMemoryUnitOfWork()

    org_id = uuid4()
    owner_1 = CompanyBuilder().with_role(CompanyType.OWN).with_organization_id(org_id).build()
    owner_2 = CompanyBuilder().with_role(CompanyType.OWN).with_organization_id(org_id).build()
    uow.companies.add(owner_1)
    uow.companies.add(owner_2)

    fake_create_system = _FakeCreateSystemContract()
    service = BackfillSystemContractsService(create_system_contract=fake_create_system)

    service.execute(
        action=BackfillSystemContractsCommand(organization_id=org_id, actor_user_id=uuid4()),
        uow=uow,
    )

    assert len(fake_create_system.calls) == 2
    assert all(call["uow"] is uow for call in fake_create_system.calls)
