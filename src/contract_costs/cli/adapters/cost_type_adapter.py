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
