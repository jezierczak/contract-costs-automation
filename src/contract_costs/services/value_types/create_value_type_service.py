from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.value_type import ValueType
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.value_types.dto.create_value_type_command import (
    CreateValueTypeCommand,
)


class CreateValueTypeService:

    def __init__(
        self,
        repository: ValueTypeRepository,
        *,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, command: CreateValueTypeCommand) -> None:
        # --- uniqueness (per org) ---
        existing = self._repository.get_by_code(
            organization_id=command.organization_id,
            code=command.code,
        )
        if existing:
            raise ValueError(
                f"ValueType with code '{command.code}' already exists"
            )

        now = self._clock()

        value_type = ValueType(
            id=self._id_generator(),
            organization_id=command.organization_id,
            code=command.code,
            name=command.name,
            description=command.description,
            direction=command.direction,
            is_active=command.is_active,
            created_at=now,
            created_by_user_id=command.actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
        )

        self._repository.add(value_type)
