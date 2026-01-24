from uuid import uuid4
import pytest

from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.services.value_types.apply.change_value_type_code_service import ChangeCostTypeCodeService
from contract_costs.services.value_types.apply.commands.change_value_type_code_command import ChangeValueTypeCodeCommand


def test_change_value_type_code(repo):
    ct = ValueType(
        id=uuid4(),
        code="OLD",
        name="Old name",
        description=None,
        direction=ValueDirection.COST,
        is_active=True,
    )
    repo.add(ct)

    service = ChangeCostTypeCodeService(repo)
    cmd = ChangeValueTypeCodeCommand(
        value_type_id=ct.id,
        new_code="NEW",
    )

    service.execute(cmd)

    updated = repo.get(ct.id)
    assert updated is not None
    assert updated.code == "NEW"


def test_change_value_type_code_duplicate_raises(repo):
    ct1 = ValueType(
        id=uuid4(),
        code="A",
        name="A",
        description=None,
        direction=ValueDirection.COST,
        is_active=True,
    )
    ct2 = ValueType(
        id=uuid4(),
        code="B",
        name="B",
        description=None,
        direction=ValueDirection.COST,
        is_active=True,
    )

    repo.add(ct1)
    repo.add(ct2)

    service = ChangeCostTypeCodeService(repo)
    cmd = ChangeValueTypeCodeCommand(
        value_type_id=ct2.id,
        new_code="A",
    )

    with pytest.raises(ValueError):
        service.execute(cmd)


def test_change_value_type_code_idempotent(repo):
    ct = ValueType(
        id=uuid4(),
        code="SAME",
        name="Same",
        description=None,
        direction=ValueDirection.COST,
        is_active=True,
    )
    repo.add(ct)

    service = ChangeCostTypeCodeService(repo)
    cmd = ChangeValueTypeCodeCommand(
        value_type_id=ct.id,
        new_code="SAME",
    )

    service.execute(cmd)

    updated = repo.get(ct.id)
    assert updated.code == "SAME"


def test_change_cost_type_code_non_existing_raises(repo):
    service = ChangeCostTypeCodeService(repo)
    cmd = ChangeValueTypeCodeCommand(
        value_type_id=uuid4(),
        new_code="X",
    )

    with pytest.raises(ValueError):
        service.execute(cmd)
