from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.identity.query.dto.list_organization_users_query import ListOrganizationUsersQuery
from contract_costs.services.identity.query.dto.organization_user_view import OrganizationUserView
from contract_costs.unit_of_work import UnitOfWork


class ListOrganizationUsersQueryService(
    ActionHandler[ListOrganizationUsersQuery, list[OrganizationUserView]]
):

    def execute(self, *, action:ListOrganizationUsersQuery, uow:UnitOfWork):
        return uow.organization_users.list_users_for_organization(
            organization_id=action.organization_id,
            active_only=False,
        )
