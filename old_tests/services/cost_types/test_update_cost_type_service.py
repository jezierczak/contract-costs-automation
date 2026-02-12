from uuid import uuid4

import pytest

from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.services.value_types.apply.commands.update_value_type_command import UpdateValueTypeCommand
from contract_costs.services.value_types.apply.update_value_type_service import UpdateValueTypeService


def test_update_value_type_changes_name_and_description(repo):
    ct = ValueType(
        id=uuid4(),
        code="MATERIAL",
        name="Old name",
        description="Old desc",
        direction=ValueDirection.COST,
        is_active=True,
    )
    repo.add(ct)

    service = UpdateValueTypeService(repo)
    cmd = UpdateValueTypeCommand(
        value_type_id=ct.id,
        name="New name",
        description="New desc",
    )

    service.execute(cmd)

    updated = repo.get(ct.id)
    assert updated is not None
    assert updated.name == "New name"
    assert updated.description == "New desc"


def test_update_non_existing_cost_type_raises(repo):
    service = UpdateValueTypeService(repo)

    cmd = UpdateValueTypeCommand(
        value_type_id=uuid4(),
        name="X",
        description=None,
    )

    with pytest.raises(ValueError):
        service.execute(cmd)
