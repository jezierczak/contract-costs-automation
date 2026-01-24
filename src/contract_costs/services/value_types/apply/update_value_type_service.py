from dataclasses import replace

from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.value_types.apply.commands.update_value_type_command import UpdateValueTypeCommand



class UpdateValueTypeService:

    def __init__(self, repository: ValueTypeRepository) -> None:
        self._repository = repository

    def execute(self, cmd: UpdateValueTypeCommand) -> None:
        value_type = self._repository.get(cmd.value_type_id)
        if value_type is None:
            raise ValueError("Value type does not exist")

        updated = replace(
            value_type,
            name=cmd.name,
            description=cmd.description,
        )

        self._repository.update(updated)
