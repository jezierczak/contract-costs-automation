from dataclasses import replace

from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.services.cost_types.apply.commands.deactivate_cost_type_command import DeactivateCostTypeCommand


class DeactivateCostTypeService:

    def __init__(self, repository: CostTypeRepository) -> None:
        self._repository = repository

    def execute(self, cmd: DeactivateCostTypeCommand) -> None:
        cost_type = self._repository.get(cmd.cost_type_id)
        if cost_type is None:
            raise ValueError("Cost type does not exist")

        if not cost_type.is_active:
            return  # idempotent

        updated = replace(cost_type, is_active=False)
        self._repository.update(updated)
