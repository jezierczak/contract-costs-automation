from uuid import uuid4

import pytest

from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.services.value_types.apply.commands.deactivate_value_type_command import DeactivateValueTypeCommand
from contract_costs.services.value_types.apply.deactivate_value_type_service import DeactivateValueTypeService


def test_deactivate_value_type(repo):
    ct = ValueType(
        id=uuid4(),
        code="SALARY",
        name="Salary",
        description=None,
        direction=ValueDirection.COST,
        is_active=True,
    )
    repo.add(ct)

    service = DeactivateValueTypeService(repo)
    cmd = DeactivateValueTypeCommand(value_type_id=ct.id)

    service.execute(cmd)

    updated = repo.get(ct.id)
    assert updated is not None
    assert updated.is_active is False


def test_deactivate_is_idempotent(repo):
    ct = ValueType(
        id=uuid4(),
        code="TRANSPORT",
        name="Transport",
        description=None,
        direction=ValueDirection.COST,
        is_active=False,
    )
    repo.add(ct)

    service = DeactivateValueTypeService(repo)
    cmd = DeactivateValueTypeCommand(value_type_id=ct.id)

    service.execute(cmd)

    updated = repo.get(ct.id)
    assert updated.is_active is False


def test_deactivate_non_existing_cost_type_raises(repo):
    service = DeactivateValueTypeService(repo)
    cmd = DeactivateValueTypeCommand(value_type_id=uuid4())

    with pytest.raises(ValueError):
        service.execute(cmd)
