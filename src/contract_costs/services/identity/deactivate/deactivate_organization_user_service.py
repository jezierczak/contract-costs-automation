from datetime import datetime
from typing import Callable

from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.services.identity.deactivate.dto.deactivate_organization_user_command import (
    DeactivateOrganizationUserCommand,
)
from contract_costs.services.identity.exceptions import (
    PermissionDenied,
    UserNotMemberOfOrganization,
)


class DeactivateOrganizationUserService:

    def __init__(
        self,
        *,
        organization_user_repo: OrganizationUserRepository,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._organization_user_repo = organization_user_repo
        self._clock = clock

    def execute(self, cmd: DeactivateOrganizationUserCommand) -> None:
        # --- actor ---
        actor = self._organization_user_repo.get_by_org_and_user(
            organization_id=cmd.organization_id,
            user_id=cmd.actor_user_id,
        )
        if not actor:
            raise PermissionDenied("User is not a member of this organization")

        if actor.role not in (OrganizationRole.OWNER, OrganizationRole.ADMIN):
            raise PermissionDenied("Only OWNER or ADMIN can deactivate users")

        # --- target ---
        target = self._organization_user_repo.get_by_org_and_user(
            organization_id=cmd.organization_id,
            user_id=cmd.target_user_id,
        )
        if not target:
            raise UserNotMemberOfOrganization()

        if target.role == OrganizationRole.OWNER:
            raise PermissionDenied("Cannot deactivate OWNER")

        if not target.is_active:
            return  # idempotent

        now = self._clock()

        updated = target.__class__(
            **{
                **target.__dict__,
                "is_active": False,
                "updated_at": now,
                "updated_by_user_id": cmd.actor_user_id,
            }
        )

        self._organization_user_repo.update(updated)
