from datetime import datetime
from typing import Callable

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


class RemoveOrganizationUserService:

    def __init__(
        self,
        *,
        organization_user_repo: OrganizationUserRepository,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._organization_user_repo = organization_user_repo
        self._clock = clock

    def execute(self, cmd: RemoveOrganizationUserCommand) -> None:
        # --- actor membership ---
        actor_membership = self._organization_user_repo.get_by_org_and_user(
            organization_id=cmd.organization_id,
            user_id=cmd.actor_user_id,
        )
        if not actor_membership:
            raise PermissionDenied("User is not a member of this organization")

        if actor_membership.role not in (
            OrganizationRole.OWNER,
            OrganizationRole.ADMIN,
        ):
            raise PermissionDenied("Only OWNER or ADMIN can remove users")

        # --- target membership ---
        target_membership = self._organization_user_repo.get_by_org_and_user(
            organization_id=cmd.organization_id,
            user_id=cmd.target_user_id,
        )
        if not target_membership:
            raise UserNotMemberOfOrganization()

        if target_membership.role == OrganizationRole.OWNER:
            raise PermissionDenied("Cannot remove organization OWNER")

        if not target_membership.is_active:
            # już usunięty → idempotencja
            return

        now = self._clock()

        removed = target_membership.__class__(  # frozen dataclass
            **{
                **target_membership.__dict__,
                "is_active": False,
                "updated_at": now,
                "updated_by_user_id": cmd.actor_user_id,
            }
        )

        self._organization_user_repo.update(removed)
