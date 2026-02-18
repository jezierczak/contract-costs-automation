from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.value_type import ValueType
from contract_costs.services.value_types.dto.create_value_type_command import (
    CreateValueTypeCommand,
)
from contract_costs.unit_of_work import UnitOfWork


class CreateValueTypeService(
    ActionHandler[CreateValueTypeCommand, UUID]
):

    def __init__(
        self,
        *,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._id_generator = id_generator
        self._clock = clock

    def execute(
        self,
        *,
        action: CreateValueTypeCommand,
        uow: UnitOfWork,
    ) -> UUID:

        value_type_repo = uow.value_types

        existing = value_type_repo.get_by_code(
            organization_id=action.organization_id,
            code=action.code,
        )
        if existing:
            raise ValueError(
                f"ValueType with code '{action.code}' already exists"
            )

        now = self._clock()

        value_type = ValueType(
            id=self._id_generator(),
            organization_id=action.organization_id,
            code=action.code,
            name=action.name,
            description=action.description,
            direction=action.direction,
            is_active=action.is_active,
            created_at=now,
            created_by_user_id=action.actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
        )

        value_type_repo.add(value_type)

        return value_type.id