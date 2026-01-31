from datetime import datetime
from typing import Callable

from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.services.identity.accept.dto.accept_organization_invite_command import (
    AcceptOrganizationInviteCommand,
)
from contract_costs.services.identity.exceptions import PermissionDenied


class AcceptOrganizationInviteService:

    def __init__(
        self,
        *,
        organization_user_repo: OrganizationUserRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._organization_user_repo = organization_user_repo
        self._clock = clock

    def execute(self, cmd: AcceptOrganizationInviteCommand) -> None:
        membership = self._organization_user_repo.get_by_org_and_user(
            organization_id=cmd.organization_id,
            user_id=cmd.user_id,
        )

        if not membership:
            raise PermissionDenied("User is not a member of this organization")

        # OWNER is accepted implicitly
        if membership.role == OrganizationRole.OWNER:
            return

        # already accepted → no-op
        if membership.accepted_at is not None:
            return

        now = self._clock()

        updated = membership.__class__(
            **{
                **membership.__dict__,
                "accepted_at": now,
                "updated_at": now,
                "updated_by_user_id": cmd.user_id,
            }
        )

        self._organization_user_repo.update(updated)
