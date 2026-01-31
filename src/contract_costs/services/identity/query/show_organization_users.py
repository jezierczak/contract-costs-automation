from uuid import UUID

from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.services.identity.query.dto.organization_user_view import OrganizationUserView


class ShowOrganizationUsersQueryService:

    def __init__(
        self,
        *,
        organization_user_repo: OrganizationUserRepository,
        user_repo: UserRepository,
    ):
        self._organization_user_repo=organization_user_repo
        self._user_repo=user_repo

    def execute(self, organization_id: UUID) -> list[OrganizationUserView]:
        memberships = self._organization_user_repo.list_by_organization(
            organization_id,
            active_only=False,
        )

        users = {
            u.id: u
            for u in self._user_repo.list(active_only=False)
        }

        result = []
        for m in memberships:
            user = users.get(m.user_id)
            if not user:
                continue  # defensive

            result.append(
                OrganizationUserView(
                    user_id=user.id,
                    login=user.login,
                    full_name=user.full_name,
                    email=user.email,
                    role=m.role,
                    is_active=m.is_active,
                    invited_at=m.invited_at,
                    accepted_at=m.accepted_at,
                )
            )

        return result
