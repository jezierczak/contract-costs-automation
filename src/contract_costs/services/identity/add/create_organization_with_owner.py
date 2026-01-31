from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization import Organization
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.model.identity.user import User
from contract_costs.repository.identity.organization_repository import OrganizationRepository
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.services.identity.add.dto.create_organization_command import CreateOrganizationCommand
from contract_costs.services.identity.exceptions import OrganizationAlreadyExists, UserAlreadyExists


class CreateOrganizationWithOwnerService:

    def __init__(
        self,
        *,
        organization_repo: OrganizationRepository,
        user_repo: UserRepository,
        organization_user_repo: OrganizationUserRepository,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,
    ):
        self._organization_repo = organization_repo
        self._user_repo = user_repo
        self._organization_user_repo = organization_user_repo
        self._id_generator = id_generator
        self._clock = clock

    def execute(self, cmd: CreateOrganizationCommand) -> UUID:
        if self._organization_repo.get_by_code(cmd.organization_code):
            raise OrganizationAlreadyExists()

        if self._user_repo .get_by_login(cmd.owner_login):
            raise UserAlreadyExists()

        now = self._clock()

        org = Organization(
            id=self._id_generator(),
            code=cmd.organization_code,
            name=cmd.organization_name,
            is_active=True,
            created_at=now,
            created_by_user_id=cmd.created_by_user_id,
            updated_at=None,
            updated_by_user_id=None,
            settings=None,
        )

        user = User(
            id=self._id_generator(),
            login=cmd.owner_login,
            email=cmd.owner_email,
            full_name=cmd.owner_full_name,
            is_active=True,
            created_at=now,
            created_by_user_id=cmd.created_by_user_id,
        )

        membership = OrganizationUser(
            id=self._id_generator(),
            organization_id=org.id,
            user_id=user.id,
            role=OrganizationRole.OWNER,
            is_active=True,
            created_at=now,
            accepted_at=now,
            created_by_user_id=cmd.created_by_user_id,
        )

        # TRANSAKCJA
        self._organization_repo.add_with_owner(
            organization=org,
            owner=user,
            membership=membership,
        )

        return org.id
