from contract_costs.model.cost_type import CostType
from contract_costs.services.cost_types.apply.commands.deactivate_cost_type_command import DeactivateCostTypeCommand
from contract_costs.services.cost_types.apply.commands.update_cost_type_command import UpdateCostTypeCommand
from contract_costs.services.cost_types.apply.deactivate_cost_type_service import DeactivateCostTypeService
from contract_costs.services.cost_types.apply.update_cost_type_service import UpdateCostTypeService
from contract_costs.services.cost_types.create_cost_type_service import (
    CreateCostTypeService,
)


def create_cost_type_from_cli(
    *,
    data: dict,
    create_cost_type_service: CreateCostTypeService,
) -> None:
    create_cost_type_service.execute(
        code=data["code"],
        name=data["name"],
        description=data.get("description"),
        is_active=data["is_active"],
    )

def update_cost_type_from_cli(
    *,
    cost_type: CostType,
    data: dict,
    update_cost_type_service: UpdateCostTypeService,
) -> None:
    cmd = UpdateCostTypeCommand(
        cost_type_id=cost_type.id,
        name=data["name"],
        description=data.get("description"),
    )

    update_cost_type_service.execute(cmd)


def deactivate_cost_type_from_cli(
    *,
    cost_type: CostType,
    deactivate_cost_type_service: DeactivateCostTypeService,
) -> None:
    cmd = DeactivateCostTypeCommand(cost_type_id=cost_type.id)
    deactivate_cost_type_service.execute(cmd)
