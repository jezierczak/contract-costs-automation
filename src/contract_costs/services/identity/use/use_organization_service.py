from contract_costs.common.context.context_provider import ContextProvider
from contract_costs.repository.identity.organization_repository import OrganizationRepository
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.services.identity.use.dto.use_organization_command import UseOrganizationCommand
from contract_costs.services.identity.exceptions import (
    OrganizationNotFound,
    UserNotMemberOfOrganization,
)

class UseOrganizationService:

    def __init__(
        self,
        *,
        organization_repo: OrganizationRepository,
        organization_user_repo: OrganizationUserRepository,
        context: ContextProvider,
    ) -> None:
        self._organization_repo = organization_repo
        self._organization_user_repo = organization_user_repo
        self._context = context

    def execute(self, cmd: UseOrganizationCommand) -> None:
        org = self._organization_repo.get_by_code(cmd.organization_code)
        if not org or not org.is_active:
            raise OrganizationNotFound(cmd.organization_code)

        membership = self._organization_user_repo.get_by_org_and_user(
            organization_id=org.id,
            user_id=cmd.user_id,
        )

        if not membership or not membership.is_active:
            raise UserNotMemberOfOrganization()

        self._context.set_current_organization(org.id)
