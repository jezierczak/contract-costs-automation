from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.user import User
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.services.identity.add.dto.create_user_command import CreateUserCommand
from contract_costs.services.identity.exceptions import UserAlreadyExists


class CreateUserService:

    def __init__(
        self,
        *,
        user_repo: UserRepository,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._user_repo = user_repo
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, cmd: CreateUserCommand) -> UUID:
        if self._user_repo.get_by_login(cmd.login):
            raise UserAlreadyExists()

        now = self._clock()

        user = User(
            id=self._id_generator(),
            login=cmd.login,
            email=cmd.email,
            full_name=cmd.full_name,
            is_active=True,
            created_at=now,
            created_by_user_id=cmd.created_by_user_id,
        )

        self._user_repo.add(user)
        return user.id
