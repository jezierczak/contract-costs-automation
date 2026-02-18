from dataclasses import replace
from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.services.value_types.apply.commands.deactivate_value_type_command import (
    DeactivateValueTypeCommand,
)
from contract_costs.unit_of_work import UnitOfWork


class DeactivateValueTypeService(
    ActionHandler[DeactivateValueTypeCommand, None]
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
        action: DeactivateValueTypeCommand,
        uow: UnitOfWork,
    ) -> None:

        repo = uow.value_types

        value_type = repo.get(
            organization_id=action.organization_id,
            value_type_id=action.value_type_id,
        )

        if value_type is None:
            raise ValueError("Value type does not exist")

        if not value_type.is_active:
            return  # idempotent

        updated = replace(
            value_type,
            is_active=False,
            updated_at=self._clock(),
            updated_by_user_id=action.actor_user_id,
        )

        repo.update(updated)