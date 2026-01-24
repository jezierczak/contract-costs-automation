from dataclasses import replace

from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.value_types.apply.commands.change_value_type_code_command import ChangeValueTypeCodeCommand


class ChangeCostTypeCodeService:

    def __init__(self, repository: ValueTypeRepository) -> None:
        self._repository = repository

    def execute(self, cmd: ChangeValueTypeCodeCommand) -> None:
        value_type = self._repository.get(cmd.value_type_id)
        if value_type is None:
            raise ValueError("Value type does not exist")

        existing = self._repository.get_by_code(cmd.new_code)
        if existing and existing.id != value_type.id:
            raise ValueError(f"Value type with code '{cmd.new_code}' already exists")

        if value_type.code == cmd.new_code:
            return  # idempotent

        updated = replace(value_type, code=cmd.new_code)
        self._repository.update(updated)
