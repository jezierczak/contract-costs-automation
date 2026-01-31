from uuid import UUID

from contract_costs.repository.identity.organization_repository import OrganizationRepository
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.services.identity.query.dto.organization_list_item_dto import OrganizationListItemDTO


class ShowOrganizationsQueryService:

    def __init__(
        self,
        *,
        organization_repo: OrganizationRepository,
        organization_user_repo: OrganizationUserRepository,
    ) -> None:
        self._organization_repo = organization_repo
        self._organization_user_repo = organization_user_repo

    def list_for_user(self, *, user_id: UUID) -> list[OrganizationListItemDTO]:
        memberships = self._organization_user_repo.list_by_user(
            user_id,
            active_only=True,
        )

        result: list[OrganizationListItemDTO] = []

        for m in memberships:
            org = self._organization_repo.get(m.organization_id)
            if not org:
                continue

            result.append(
                OrganizationListItemDTO(
                    id=org.id,
                    code=org.code,
                    name=org.name,
                    is_active=org.is_active,
                    role=m.role.value,
                )
            )

        return result
