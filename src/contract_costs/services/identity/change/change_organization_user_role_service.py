from datetime import datetime
from typing import Callable

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.time import utc_now
from contract_costs.services.identity.change.dto.change_organization_user_role_command import (
    ChangeOrganizationUserRoleCommand,
)
from contract_costs.services.identity.exceptions import (
    PermissionDenied,
    UserNotMemberOfOrganization,
)
from contract_costs.unit_of_work import UnitOfWork



class ChangeOrganizationUserRoleService(ActionHandler[ChangeOrganizationUserRoleCommand,None]):

    def __init__(
        self,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._clock = clock

    def execute(self,*,
                action: ChangeOrganizationUserRoleCommand,
                uow:UnitOfWork
                ) -> None:
        organization_user_repo=uow.organization_users
        # --- actor ---
        actor = organization_user_repo.get_by_org_and_user(
            organization_id=action.organization_id,
            user_id=action.actor_user_id,
        )
        if not actor:
            raise PermissionDenied("User is not a member of this organization")

        # --- target ---
        target = organization_user_repo.get_by_org_and_user(
            organization_id=action.organization_id,
            user_id=action.target_user_id,
        )
        if not target:
            raise UserNotMemberOfOrganization()

        updated = target.change_role(
            new_role=action.new_role,
            actor_role=actor.role,
            now=self._clock(),
            by_user_id=action.actor_user_id,
        )

        if updated != target:
            uow.organization_users.update(updated)
