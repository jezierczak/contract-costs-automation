from contract_costs.model.value_direction import ValueDirection
from contract_costs.model.value_type import ValueType
from contract_costs.services.value_types.apply.commands.deactivate_value_type_command import DeactivateValueTypeCommand
from contract_costs.services.value_types.apply.commands.update_value_type_command import UpdateValueTypeCommand
from contract_costs.services.value_types.apply.deactivate_value_type_service import DeactivateValueTypeService
from contract_costs.services.value_types.apply.update_value_type_service import UpdateValueTypeService
from contract_costs.services.value_types.create_value_type_service import (
    CreateValueTypeService,
)


def create_value_type_from_cli(
    *,
    data: dict,
    create_value_type_service: CreateValueTypeService,
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
    create_value_type_service.execute(
        code=data["code"],
        name=data["name"],
        description=data.get("description"),
        direction=direction,
        is_active=data["is_active"],
    )

def update_value_type_from_cli(
    *,
    value_type: ValueType,
    data: dict,
    update_value_type_service: UpdateValueTypeService,
) -> None:
    cmd = UpdateValueTypeCommand(
        value_type_id=value_type.id,
        name=data["name"],
        description=data.get("description"),
    )

    update_value_type_service.execute(cmd)


def deactivate_value_type_from_cli(
    *,
    value_type: ValueType,
    deactivate_value_type_service: DeactivateValueTypeService,
) -> None:
    cmd = DeactivateValueTypeCommand(value_type_id=value_type.id)
    deactivate_value_type_service.execute(cmd)
