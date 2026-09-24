from dataclasses import replace
from datetime import date
from uuid import uuid4

import pytest

from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.contracts.dto.update_contract_command import UpdateContractCommand
from contract_costs.services.contracts.update_contract_service import UpdateContractService
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.builders.contract_builder import ContractBuilder
from tests.helpers.contract_commands import make_contract_command
from tests.helpers.contracts_helpers import FakeContractNodeTreeBuilder, FakeValidator


def _update_command(contract, *, start_date, end_date) -> UpdateContractCommand:
    return UpdateContractCommand(
        organization_id=contract.organization_id,
        actor_user_id=uuid4(),
        contract_id=contract.id,
        code=contract.code,
        name=contract.name,
        description=contract.description,
        owner=contract.owner,
        client=contract.client,
        start_date=start_date,
        end_date=end_date,
    )


def test_update_contract_sets_dates():
    uow = InMemoryUnitOfWork()
    contract = ContractBuilder().with_start_date(None).with_end_date(None).build()
    uow.contracts.add(contract)

    UpdateContractService().execute(
        action=_update_command(contract, start_date=date(2026, 1, 1), end_date=date(2026, 12, 31)),
        uow=uow,
    )

    updated = uow.contracts.get(organization_id=contract.organization_id, contract_id=contract.id)
    assert updated.start_date == date(2026, 1, 1)
    assert updated.end_date == date(2026, 12, 31)


def test_update_contract_rejects_end_before_start():
    uow = InMemoryUnitOfWork()
    contract = ContractBuilder().build()
    uow.contracts.add(contract)

    with pytest.raises(ValueError, match="zakończenia"):
        UpdateContractService().execute(
            action=_update_command(contract, start_date=date(2026, 6, 1), end_date=date(2026, 5, 31)),
            uow=uow,
        )


def test_create_contract_rejects_end_before_start(uow):
    service = CreateContractService(
        contract_node_tree_builder=FakeContractNodeTreeBuilder(nodes_to_return=[]),
        contract_node_tree_validator=FakeValidator(),
    )
    cmd = replace(
        make_contract_command(contract_node_input=[]),
        start_date=date(2026, 6, 1),
        end_date=date(2026, 5, 31),
    )

    with pytest.raises(ValueError, match="zakończenia"):
        service.execute(action=cmd, uow=uow)
