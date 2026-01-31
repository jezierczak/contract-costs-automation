from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.repository.identity.organization_repository import OrganizationRepository
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.services.identity.add.dto.assign_user_to_organization_command import AssignUserToOrganizationCommand

from contract_costs.services.identity.exceptions import (
    OrganizationNotFound,
    UserNotFound,
    UserAlreadyInOrganization, PermissionDenied,
)


class AddOrganizationUserService:

    def __init__(
        self,
        *,
        organization_repo: OrganizationRepository,
        user_repo: UserRepository,
        organization_user_repo: OrganizationUserRepository,
        id_generator: Callable[[], UUID]=new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._organization_repo = organization_repo
        self._user_repo = user_repo
        self._organization_user_repo = organization_user_repo
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, cmd: AssignUserToOrganizationCommand) -> UUID:
        # --- validate organization ---
        actor_membership = self._organization_user_repo.get_by_org_and_user(
            organization_id=cmd.organization_id,
            user_id=cmd.actor_user_id,
        )

        if not actor_membership:
            raise PermissionDenied("User is not a member of this organization")

        if actor_membership.role not in (OrganizationRole.OWNER, OrganizationRole.ADMIN):
            raise PermissionDenied("Only OWNER or ADMIN can add users")

        if not self._organization_repo.exists(cmd.organization_id):
            raise OrganizationNotFound()

        # --- validate user ---
        user = self._user_repo.get(cmd.target_user_id)
        if not user:
            raise UserNotFound()

        # --- already member? ---
        if self._organization_user_repo.exists(
            organization_id=cmd.organization_id,
            user_id=cmd.target_user_id,
        ):
            raise UserAlreadyInOrganization()

        now = self._clock()

        membership = OrganizationUser(
            id=self._id_generator(),
            organization_id=cmd.organization_id,
            user_id=cmd.target_user_id,
            role=cmd.role,
            is_active=True,
            created_at=now,
            created_by_user_id=cmd.actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
            invited_at=None,
            invited_by_user_id=None,
            accepted_at=None,
        )

        self._organization_user_repo.add(membership)

        return membership.id
