from dataclasses import replace
from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.services.value_types.apply.commands.update_value_type_command import (
    UpdateValueTypeCommand,
)
from contract_costs.unit_of_work import UnitOfWork


class UpdateValueTypeService(
    ActionHandler[UpdateValueTypeCommand, None]
):

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._clock = clock

    def execute(
        self,
        *,
        action: UpdateValueTypeCommand,
        uow: UnitOfWork,
    ) -> None:

        repo = uow.value_types

        value_type = repo.get(
            organization_id=action.organization_id,
            value_type_id=action.value_type_id,
        )
        if value_type is None:
            raise ValueError("Value type does not exist")

        if value_type.name == action.name and value_type.description == action.description and value_type.code == action.code and value_type.direction == action.direction:
            return

        updated = replace(
            value_type,
            name=action.name,
            description=action.description,
            code=action.code,
            direction=action.direction,
            updated_at=self._clock(),
            updated_by_user_id=action.actor_user_id,
        )

        repo.update(updated)