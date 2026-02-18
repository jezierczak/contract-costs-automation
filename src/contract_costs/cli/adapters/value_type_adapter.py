from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_bus import ActionBus
from contract_costs.common.time import utc_now
from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.services.value_types.apply.commands.deactivate_value_type_command import DeactivateValueTypeCommand
from contract_costs.services.value_types.apply.commands.update_value_type_command import UpdateValueTypeCommand
from contract_costs.services.value_types.apply.deactivate_value_type_service import DeactivateValueTypeService
from contract_costs.services.value_types.apply.update_value_type_service import UpdateValueTypeService
from contract_costs.services.value_types.create_value_type_service import (
    CreateValueTypeService,
)
from contract_costs.services.value_types.dto.create_value_type_command import CreateValueTypeCommand


def create_value_type_from_cli(
    *,
    data: dict,
    organization_id,
    actor_user_id,
    create_value_type_service: CreateValueTypeService,
    action_bus:ActionBus,
) -> None:
    raw = data.get("direction")
    if not raw:
        raise ValueError("Direction is required")

    v = raw.strip().lower()
    if v in ("c", "cost"):
        direction = ValueDirection.COST
    elif v in ("r", "revenue"):
        direction = ValueDirection.REVENUE
    elif v in ("i", "internal"):
        direction = ValueDirection.INTERNAL
    else:
        raise ValueError("Direction must be COST, REVENUE or INTERNAL (c/r/i)")

    cmd = CreateValueTypeCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        code=data["code"],
        name=data["name"],
        description=data.get("description"),
        direction=direction,
        is_active=data["is_active"],
    )

    action_bus.execute(action=cmd,handler=create_value_type_service)



def update_value_type_from_cli(
    *,
    value_type: ValueType,
    data: dict,
    organization_id,
    actor_user_id,
    update_value_type_service: UpdateValueTypeService,
    action_bus:ActionBus,
) -> None:
    cmd = UpdateValueTypeCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        value_type_id=value_type.id,
        name=data["name"],
        description=data.get("description"),
    )

    action_bus.execute(action=cmd, handler=update_value_type_service)


def deactivate_value_type_from_cli(
    *,
    value_type: ValueType,
    organization_id,
    actor_user_id,
    deactivate_value_type_service: DeactivateValueTypeService,
    action_bus:ActionBus,
) -> None:
    cmd = DeactivateValueTypeCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        value_type_id=value_type.id,
    )
    action_bus.execute(action=cmd, handler=deactivate_value_type_service)
