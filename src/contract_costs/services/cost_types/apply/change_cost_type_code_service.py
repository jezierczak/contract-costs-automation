from dataclasses import replace

from contract_costs.repository.cost_type_repository import CostTypeRepository
from contract_costs.services.cost_types.apply.commands.change_cost_type_code_command import ChangeCostTypeCodeCommand


class ChangeCostTypeCodeService:

    def __init__(self, repository: CostTypeRepository) -> None:
        self._repository = repository

    def execute(self, cmd: ChangeCostTypeCodeCommand) -> None:
        cost_type = self._repository.get(cmd.cost_type_id)
        if cost_type is None:
            raise ValueError("Cost type does not exist")

        existing = self._repository.get_by_code(cmd.new_code)
        if existing and existing.id != cost_type.id:
            raise ValueError(f"Cost type with code '{cmd.new_code}' already exists")

        if cost_type.code == cmd.new_code:
            return  # idempotent

        updated = replace(cost_type, code=cmd.new_code)
        self._repository.update(updated)
