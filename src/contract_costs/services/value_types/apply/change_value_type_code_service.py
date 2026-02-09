from dataclasses import replace
from datetime import datetime
from typing import Callable

from contract_costs.common.time import utc_now
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.value_types.apply.commands.change_value_type_code_command import ChangeValueTypeCodeCommand


class ChangeValueTypeCodeService:

    def __init__(self, repository: ValueTypeRepository, clock: Callable[[],datetime] = utc_now) -> None:
        self._repository = repository
        self._clock = clock

    def execute(self, cmd: ChangeValueTypeCodeCommand) -> None:
        value_type = self._repository.get(organization_id=cmd.organization_id,
                                          value_type_id=cmd.value_type_id)
        if value_type is None:
            raise ValueError("Value type does not exist")

        existing = self._repository.get_by_code(
                                                organization_id=cmd.organization_id,
                                                code=cmd.new_code)
        if existing and existing.id != value_type.id:
            raise ValueError(f"Value type with code '{cmd.new_code}' already exists")

        if value_type.code == cmd.new_code:
            return  # idempotent

        updated = replace(value_type,
                            code=cmd.new_code,
                            updated_at = self._clock(),
                            updated_by_user_id = cmd.actor_user_id
                          )
        self._repository.update(updated)
