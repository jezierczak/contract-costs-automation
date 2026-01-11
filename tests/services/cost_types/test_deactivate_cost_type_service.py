from uuid import uuid4

import pytest

from contract_costs.model.cost_type import CostType
from contract_costs.services.cost_types.apply.commands.deactivate_cost_type_command import DeactivateCostTypeCommand
from contract_costs.services.cost_types.apply.deactivate_cost_type_service import DeactivateCostTypeService


def test_deactivate_cost_type(repo):
    ct = CostType(
        id=uuid4(),
        code="SALARY",
        name="Salary",
        description=None,
        is_active=True,
    )
    repo.add(ct)

    service = DeactivateCostTypeService(repo)
    cmd = DeactivateCostTypeCommand(cost_type_id=ct.id)

    service.execute(cmd)

    updated = repo.get(ct.id)
    assert updated is not None
    assert updated.is_active is False


def test_deactivate_is_idempotent(repo):
    ct = CostType(
        id=uuid4(),
        code="TRANSPORT",
        name="Transport",
        description=None,
        is_active=False,
    )
    repo.add(ct)

    service = DeactivateCostTypeService(repo)
    cmd = DeactivateCostTypeCommand(cost_type_id=ct.id)

    service.execute(cmd)

    updated = repo.get(ct.id)
    assert updated.is_active is False


def test_deactivate_non_existing_cost_type_raises(repo):
    service = DeactivateCostTypeService(repo)
    cmd = DeactivateCostTypeCommand(cost_type_id=uuid4())

    with pytest.raises(ValueError):
        service.execute(cmd)
