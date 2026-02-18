from datetime import datetime
from uuid import uuid4

import pytest

from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.value_types.create_value_type_service import (
    CreateValueTypeService,
)
from contract_costs.services.value_types.dto.create_value_type_command import (
    CreateValueTypeCommand,
)


def test_create_value_type_adds_item_with_generated_id_and_audit(value_type_repo, uow):
    fixed_id = uuid4()
    fixed_time = datetime(2026, 2, 12, 21, 0, 0)
    organization_id = uuid4()
    actor_user_id = uuid4()

    service = CreateValueTypeService(
        id_generator=lambda: fixed_id,
        clock=lambda: fixed_time,
    )

    service.execute(
        action=CreateValueTypeCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            code="MATERIAL",
            name="Material",
            description="Zakup materialow",
            direction=ValueDirection.COST,
            is_active=True,
        ),
        uow=uow,
    )

    saved = value_type_repo.get(
        organization_id=organization_id,
        value_type_id=fixed_id,
    )

    assert saved is not None
    assert saved.code == "MATERIAL"
    assert saved.direction == ValueDirection.COST
    assert saved.created_at == fixed_time
    assert saved.created_by_user_id == actor_user_id


def test_create_value_type_raises_when_code_already_exists(uow):
    organization_id = uuid4()

    service = CreateValueTypeService()
    cmd = CreateValueTypeCommand(
        organization_id=organization_id,
        actor_user_id=uuid4(),
        code="SERVICE",
        name="Service",
        description=None,
        direction=ValueDirection.COST,
        is_active=True,
    )

    service.execute(action=cmd, uow=uow)

    with pytest.raises(ValueError, match="already exists"):
        service.execute(action=cmd, uow=uow)
