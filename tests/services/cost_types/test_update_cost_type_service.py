from uuid import uuid4

import pytest

from contract_costs.model.cost_type import CostType
from contract_costs.services.cost_types.apply.commands.update_cost_type_command import UpdateCostTypeCommand
from contract_costs.services.cost_types.apply.update_cost_type_service import UpdateCostTypeService


def test_update_cost_type_changes_name_and_description(repo):
    ct = CostType(
        id=uuid4(),
        code="MATERIAL",
        name="Old name",
        description="Old desc",
        is_active=True,
    )
    repo.add(ct)

    service = UpdateCostTypeService(repo)
    cmd = UpdateCostTypeCommand(
        cost_type_id=ct.id,
        name="New name",
        description="New desc",
    )

    service.execute(cmd)

    updated = repo.get(ct.id)
    assert updated is not None
    assert updated.name == "New name"
    assert updated.description == "New desc"


def test_update_non_existing_cost_type_raises(repo):
    service = UpdateCostTypeService(repo)

    cmd = UpdateCostTypeCommand(
        cost_type_id=uuid4(),
        name="X",
        description=None,
    )

    with pytest.raises(ValueError):
        service.execute(cmd)
