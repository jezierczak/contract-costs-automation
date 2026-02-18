from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.common.context.context_provider import ContextProvider
from contract_costs.services.identity.use.dto.use_organization_command import UseOrganizationCommand
from contract_costs.services.identity.exceptions import (
    OrganizationNotFound,
    UserNotMemberOfOrganization,
)
from contract_costs.unit_of_work import UnitOfWork


class UseOrganizationService(
    ActionHandler[UseOrganizationCommand, None]
):

    def __init__(self, context: ContextProvider):
        self._context = context

    def execute(self, *, action:UseOrganizationCommand, uow:UnitOfWork) -> None:
        org = uow.organizations.get_by_code(action.organization_code)
        if not org or not org.is_active:
            raise OrganizationNotFound(action.organization_code)

        membership = uow.organization_users.get_by_org_and_user(
            organization_id=org.id,
            user_id=action.actor_user_id,
        )

        if not membership or not membership.is_active:
            raise UserNotMemberOfOrganization()

        self._context.set_current_organization(org.id)
