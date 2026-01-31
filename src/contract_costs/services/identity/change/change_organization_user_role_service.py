from datetime import datetime
from typing import Callable

from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.services.identity.change.dto.change_organization_user_role_command import (
    ChangeOrganizationUserRoleCommand,
)
from contract_costs.services.identity.exceptions import (
    PermissionDenied,
    UserNotMemberOfOrganization,
)


class ChangeOrganizationUserRoleService:

    def __init__(
        self,
        *,
        organization_user_repo: OrganizationUserRepository,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._organization_user_repo = organization_user_repo
        self._clock = clock

    def execute(self, cmd: ChangeOrganizationUserRoleCommand) -> None:
        # --- actor ---
        actor = self._organization_user_repo.get_by_org_and_user(
            organization_id=cmd.organization_id,
            user_id=cmd.actor_user_id,
        )
        if not actor:
            raise PermissionDenied("User is not a member of this organization")

        if actor.role not in (OrganizationRole.OWNER, OrganizationRole.ADMIN):
            raise PermissionDenied("Only OWNER or ADMIN can change roles")

        # --- target ---
        target = self._organization_user_repo.get_by_org_and_user(
            organization_id=cmd.organization_id,
            user_id=cmd.target_user_id,
        )
        if not target:
            raise UserNotMemberOfOrganization()

        if target.role == OrganizationRole.OWNER:
            raise PermissionDenied("Cannot change role of OWNER")

        if actor.role == OrganizationRole.ADMIN and target.role == OrganizationRole.OWNER:
            raise PermissionDenied("ADMIN cannot change OWNER")

        if target.role == cmd.new_role:
            return  # idempotent

        now = self._clock()

        updated = target.__class__(
            **{
                **target.__dict__,
                "role": cmd.new_role,
                "updated_at": now,
                "updated_by_user_id": cmd.actor_user_id,
            }
        )

        self._organization_user_repo.update(updated)
