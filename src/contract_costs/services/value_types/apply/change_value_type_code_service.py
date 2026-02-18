from dataclasses import replace
from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.services.value_types.apply.commands.change_value_type_code_command import (
    ChangeValueTypeCodeCommand,
)
from contract_costs.unit_of_work import UnitOfWork


class ChangeValueTypeCodeService(
    ActionHandler[ChangeValueTypeCodeCommand, None]
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
        action: ChangeValueTypeCodeCommand,
        uow: UnitOfWork,
    ) -> None:

        repo = uow.value_types

        value_type = repo.get(
            organization_id=action.organization_id,
            value_type_id=action.value_type_id,
        )
        if value_type is None:
            raise ValueError("Value type does not exist")

        existing = repo.get_by_code(
            organization_id=action.organization_id,
            code=action.new_code,
        )
        if existing and existing.id != value_type.id:
            raise ValueError(
                f"Value type with code '{action.new_code}' already exists"
            )

        if value_type.code == action.new_code:
            return  # idempotent

        updated = replace(
            value_type,
            code=action.new_code,
            updated_at=self._clock(),
            updated_by_user_id=action.actor_user_id,
        )

        repo.update(updated)