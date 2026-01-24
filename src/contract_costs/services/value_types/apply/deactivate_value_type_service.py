from dataclasses import replace

from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.value_types.apply.commands.deactivate_value_type_command import DeactivateValueTypeCommand


class DeactivateValueTypeService:

    def __init__(self, repository: ValueTypeRepository) -> None:
        self._repository = repository

    def execute(self, cmd: DeactivateValueTypeCommand) -> None:
        value_type = self._repository.get(cmd.value_type_id)
        if value_type is None:
            raise ValueError("Value type does not exist")

        if not value_type.is_active:
            return  # idempotent

        updated = replace(value_type, is_active=False)
        self._repository.update(updated)
