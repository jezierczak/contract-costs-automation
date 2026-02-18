from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.services.identity.remove.dto.remove_organization_user_command import (
    RemoveOrganizationUserCommand,
)
from contract_costs.services.identity.exceptions import (
    PermissionDenied,
    UserNotMemberOfOrganization,
)
from contract_costs.unit_of_work import UnitOfWork


class RemoveOrganizationUserService(
    ActionHandler[RemoveOrganizationUserCommand, None]
):

    def __init__(self, clock: Callable[[], datetime] = utc_now):
        self._clock = clock

    def execute(self, *, action:RemoveOrganizationUserCommand, uow:UnitOfWork) -> None:

        repo = uow.organization_users

        actor = repo.get_by_org_and_user(
            organization_id=action.organization_id,
            user_id=action.actor_user_id,
        )
        if not actor:
            raise PermissionDenied("User is not a member")

        target = repo.get_by_org_and_user(
            organization_id=action.organization_id,
            user_id=action.target_user_id,
        )
        if not target:
            raise UserNotMemberOfOrganization()

        updated = target.remove(
            actor_role=actor.role,
            now=self._clock(),
            by_user_id=action.actor_user_id,
        )

        if updated != target:
            repo.update(updated)
