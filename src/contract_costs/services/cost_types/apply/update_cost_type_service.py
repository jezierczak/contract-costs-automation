from dataclasses import replace

from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.services.cost_types.apply.commands.update_cost_type_command import UpdateCostTypeCommand



class UpdateCostTypeService:

    def __init__(self, repository: CostTypeRepository) -> None:
        self._repository = repository

    def execute(self, cmd: UpdateCostTypeCommand) -> None:
        cost_type = self._repository.get(cmd.cost_type_id)
        if cost_type is None:
            raise ValueError("Cost type does not exist")

        updated = replace(
            cost_type,
            name=cmd.name,
            description=cmd.description,
        )

        self._repository.update(updated)
