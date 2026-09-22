from datetime import datetime
from uuid import uuid4

import pytest

from contract_costs.services.value_types.apply.change_value_type_code_service import (
    ChangeValueTypeCodeService,
)
from contract_costs.services.value_types.apply.commands.change_value_type_code_command import (
    ChangeValueTypeCodeCommand,
)
from contract_costs.services.value_types.apply.commands.deactivate_value_type_command import (
    DeactivateValueTypeCommand,
)
from contract_costs.services.value_types.apply.commands.update_value_type_command import (
    UpdateValueTypeCommand,
)
from contract_costs.services.value_types.apply.deactivate_value_type_service import (
    DeactivateValueTypeService,
)
from contract_costs.services.value_types.apply.update_value_type_service import (
    UpdateValueTypeService,
)
from tests.builders.value_type_builder import ValueTypeBuilder


def test_change_code_updates_value_type(value_type_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    fixed_time = datetime(2026, 2, 12, 21, 5, 0)

    value_type = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_code("OLD")
        .build()
    )
    value_type_repo.add(value_type)

    service = ChangeValueTypeCodeService(clock=lambda: fixed_time)

    service.execute(
        action=ChangeValueTypeCodeCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            value_type_id=value_type.id,
            new_code="NEW",
        ),
        uow=uow,
    )

    updated = value_type_repo.get(
        organization_id=organization_id,
        value_type_id=value_type.id,
    )
    assert updated is not None
    assert updated.code == "NEW"
    assert updated.updated_at == fixed_time
    assert updated.updated_by_user_id == actor_user_id


def test_change_code_raises_when_new_code_is_taken(value_type_repo, uow):
    organization_id = uuid4()
    vt_a = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_code("A")
        .build()
    )
    vt_b = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_code("B")
        .build()
    )
    value_type_repo.add(vt_a)
    value_type_repo.add(vt_b)

    service = ChangeValueTypeCodeService()

    with pytest.raises(ValueError, match="already exists"):
        service.execute(
            action=ChangeValueTypeCodeCommand(
                organization_id=organization_id,
                actor_user_id=uuid4(),
                value_type_id=vt_a.id,
                new_code="B",
            ),
            uow=uow,
        )


def test_update_value_type_changes_name_and_description(value_type_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    fixed_time = datetime(2026, 2, 12, 21, 10, 0)
    value_type = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .build()
    )
    value_type_repo.add(value_type)

    service = UpdateValueTypeService(clock=lambda: fixed_time)
    service.execute(
        action=UpdateValueTypeCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            value_type_id=value_type.id,
            name="Nowa nazwa",
            description="Nowy opis",
            code=value_type.code,
            direction=value_type.direction,
        ),
        uow=uow,
    )

    updated = value_type_repo.get(
        organization_id=organization_id,
        value_type_id=value_type.id,
    )
    assert updated is not None
    assert updated.name == "Nowa nazwa"
    assert updated.description == "Nowy opis"
    assert updated.updated_at == fixed_time
    assert updated.updated_by_user_id == actor_user_id


def test_deactivate_sets_is_active_false_and_is_idempotent(value_type_repo, uow):
    organization_id = uuid4()
    actor_user_id = uuid4()
    fixed_time = datetime(2026, 2, 12, 21, 15, 0)
    value_type = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_is_active(True)
        .build()
    )
    value_type_repo.add(value_type)

    service = DeactivateValueTypeService(clock=lambda: fixed_time)

    cmd = DeactivateValueTypeCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        value_type_id=value_type.id,
    )
    service.execute(action=cmd, uow=uow)
    service.execute(action=cmd, uow=uow)

    updated = value_type_repo.get(
        organization_id=organization_id,
        value_type_id=value_type.id,
    )
    assert updated is not None
    assert updated.is_active is False
    assert updated.updated_at == fixed_time
    assert updated.updated_by_user_id == actor_user_id
