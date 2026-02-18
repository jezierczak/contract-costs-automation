from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.user import User

from contract_costs.services.identity.add.dto.create_user_command import CreateUserCommand
from contract_costs.services.identity.exceptions import UserAlreadyExists
from contract_costs.unit_of_work import UnitOfWork


class CreateUserService(
    ActionHandler[CreateUserCommand, UUID]
):

    def __init__(
        self,
        *,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._id_generator = id_generator
        self._clock = clock

    def execute(
        self,
        *,
        action: CreateUserCommand,
        uow: UnitOfWork,
    ) -> UUID:

        if uow.users.get_by_login(action.login):
            raise UserAlreadyExists()

        now = self._clock()

        user = User(
            id=self._id_generator(),
            login=action.login,
            email=action.email,
            full_name=action.full_name,
            is_active=True,
            created_at=now,
            created_by_user_id=action.actor_user_id,
        )

        uow.users.add(user)

        return user.id
