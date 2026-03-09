import logging
from datetime import datetime
from typing import Callable
from uuid import UUID

from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization import Organization
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.model.identity.user import User
from contract_costs.services.identity.add.dto.create_organization_command import CreateOrganizationCommand
from contract_costs.services.identity.exceptions import OrganizationAlreadyExists, UserAlreadyExists
from contract_costs.services.init.init_application_service import InitApplicationService
from contract_costs.unit_of_work import UnitOfWork

logger = logging.getLogger(__name__)

class CreateOrganizationWithOwnerService(
    ActionHandler[CreateOrganizationCommand, UUID]
):

    def __init__(
        self,
        *,
        init_app_service: InitApplicationService,
        id_generator: Callable[[], UUID] = new_uuid,
        clock: Callable[[], datetime] = utc_now,

    ):
        self._init_app_service = init_app_service
        self._id_generator = id_generator
        self._clock = clock

    def execute(
        self,
        *,
        action: CreateOrganizationCommand,
        uow: UnitOfWork,
    ) -> tuple[UUID,UUID]:
        organization_repo =uow.organizations
        user_repo =uow.users
        organization_users_repo = uow.organization_users

        if organization_repo.get_by_code(action.organization_code):
            raise OrganizationAlreadyExists()

        if user_repo .get_by_login(action.owner_login):
            raise UserAlreadyExists()

        now = self._clock()

        org_id = self._id_generator()
        user_id = self._id_generator()
        org_user_id = self._id_generator()
        org = Organization(
            id=org_id,
            code=action.organization_code,
            name=action.organization_name,
            is_active=True,
            created_at=now,
            created_by_user_id=action.created_by_user_id,
            updated_at=None,
            updated_by_user_id=None,
            settings=None,
        )

        user = User(
            id=user_id,
            login=action.owner_login,
            email=action.owner_email,
            full_name=action.owner_full_name,
            is_active=True,
            created_at=now,
            created_by_user_id=action.created_by_user_id,
            password_hash=action.owner_password_hash,
        )

        membership = OrganizationUser(
            id=org_user_id,
            organization_id=org.id,
            user_id=user.id,
            role=OrganizationRole.OWNER,
            is_active=True,
            created_at=now,
            accepted_at=now,
            created_by_user_id=action.created_by_user_id,
        )

        organization_repo.add(org)
        user_repo.add(user)
        organization_users_repo.add(membership)

        def _init():
            try:
                self._init_app_service.execute(organization_id=org_id)
            except Exception:
                logger.exception(
                    "Failed to initialize organization workdir",
                    extra={"organization_id": str(org_id)},
                )

        uow.add_post_commit_hook(_init)

        return org.id,user.id
