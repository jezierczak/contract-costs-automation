from dataclasses import replace
from datetime import datetime
from typing import Callable

from contract_costs.common.time import utc_now
from contract_costs.repository.value_type_repository import ValueTypeRepository
from contract_costs.services.value_types.apply.commands.update_value_type_command import UpdateValueTypeCommand



class UpdateValueTypeService:

    def __init__(self,
                 repository: ValueTypeRepository,
                clock: Callable[[], datetime] = utc_now
                 ) -> None:
        self._repository = repository
        self._clock = clock

    def execute(self, cmd: UpdateValueTypeCommand) -> None:
        value_type = self._repository.get(organization_id=cmd.organization_id,
                                          value_type_id=cmd.value_type_id)
        if value_type is None:
            raise ValueError("Value type does not exist")

        updated = replace(
            value_type,
            name=cmd.name,
            description=cmd.description,
            updated_at=self._clock(),
            updated_by_user_id=cmd.actor_user_id
        )

        self._repository.update(updated)
