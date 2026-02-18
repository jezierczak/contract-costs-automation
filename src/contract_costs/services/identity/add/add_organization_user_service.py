from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.services.identity.add.dto.assign_user_to_organization_command import AssignUserToOrganizationCommand

from contract_costs.services.identity.exceptions import (
    OrganizationNotFound,
    UserNotFound,
    UserAlreadyInOrganization, PermissionDenied,
)
from contract_costs.unit_of_work import UnitOfWork


class AddOrganizationUserService(
    ActionHandler[AssignUserToOrganizationCommand, UUID]
):


    def __init__(
        self,
        id_generator: Callable[[], UUID]=new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._id_generator = id_generator
        self._clock = clock

    def execute(self,
                *,
                action: AssignUserToOrganizationCommand,
                uow:UnitOfWork
                ) -> UUID:
        organization_repo =uow.organizations
        user_repo =uow.users
        organization_user_repo = uow.organization_users
        # --- validate organization ---
        actor_membership = organization_user_repo.get_by_org_and_user(
            organization_id=action.organization_id,
            user_id=action.actor_user_id,
        )

        if not actor_membership:
            raise PermissionDenied("User is not a member of this organization")

        # if actor_membership.role not in (OrganizationRole.OWNER, OrganizationRole.ADMIN):
        #     raise PermissionDenied("Only OWNER or ADMIN can add users")

        if not organization_repo.exists(action.organization_id):
            raise OrganizationNotFound()

        # --- validate user ---
        user = user_repo.get(action.target_user_id)
        if not user:
            raise UserNotFound()

        # --- already member? ---
        if organization_user_repo.exists(
            organization_id=action.organization_id,
            user_id=action.target_user_id,
        ):
            raise UserAlreadyInOrganization()

        now = self._clock()

        membership = OrganizationUser(
            id=self._id_generator(),
            organization_id=action.organization_id,
            user_id=action.target_user_id,
            role=action.role,
            is_active=True,
            created_at=now,
            created_by_user_id=action.actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
            invited_at=None,
            invited_by_user_id=None,
            accepted_at=None,
        )

        organization_user_repo.add(membership)

        return membership.id
