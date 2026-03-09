from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.identity.auth.password_hasher import PasswordHasher
from contract_costs.services.identity.exceptions import UserNotFound, PermissionDenied, UserInactive
from contract_costs.services.identity.auth.dto.authenticate_user_command import AuthenticateUserCommand


class AuthenticateUserService(
    ActionHandler[AuthenticateUserCommand, UUID]
):
    def __init__(self, password_hasher: PasswordHasher):
        self._password_hasher = password_hasher

    def execute(self, *, action, uow):
        user_repo = uow.users

        user = user_repo.get_by_login(action.login)
        if not user:
            raise UserNotFound()

        if not user.is_active:
            raise UserInactive()

        if not user.password_hash:
            raise PermissionDenied()

        if not self._password_hasher.verify(
                action.password,
                user.password_hash,
        ):
            raise PermissionDenied()

        return user.id
