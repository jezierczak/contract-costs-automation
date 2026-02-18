from contract_costs.action_bus.action_handler import ActionHandler
from contract_costs.services.identity.query.dto.list_user_organizations_query import ListUserOrganizationsQuery
from contract_costs.services.identity.query.dto.organization_list_item_dto import OrganizationListItemDTO
from contract_costs.unit_of_work import UnitOfWork


class ListUserOrganizationsQueryService(
    ActionHandler[ListUserOrganizationsQuery, list[OrganizationListItemDTO]]
):

    def execute(
        self,
        *,
        action: ListUserOrganizationsQuery,
        uow: UnitOfWork,
    ) -> list[OrganizationListItemDTO]:

        # Query side – bez domeny, bez replace
        return uow.organization_users.list_organizations_for_user(
            user_id=action.actor_user_id
        )
    # def list_for_user(self, *, user_id: UUID) -> list[OrganizationListItemDTO]:
    #     memberships = self._organization_user_repo.list_by_user(
    #         user_id,
    #         active_only=True,
    #     )
    #
    #     result: list[OrganizationListItemDTO] = []
    #
    #     for m in memberships:
    #         org = self._organization_repo.get(m.organization_id)
    #         if not org:
    #             continue
    #
    #         result.append(
    #             OrganizationListItemDTO(
    #                 id=org.id,
    #                 code=org.code,
    #                 name=org.name,
    #                 is_active=org.is_active,
    #                 role=m.role.value,
    #             )
    #         )
    #
    #     return result
