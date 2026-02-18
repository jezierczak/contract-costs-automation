from uuid import UUID

from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.repository.identity.organization_user_repository import (
    OrganizationUserRepository
)
from contract_costs.repository.inmemory.identity.in_memory_storage_repository import InMemoryIdentityStorage
from contract_costs.services.identity.query.dto.organization_list_item_dto import OrganizationListItemDTO
from contract_costs.services.identity.query.dto.organization_user_view import OrganizationUserView


class InMemoryOrganizationUserRepository(OrganizationUserRepository):

    def __init__(self, storage: InMemoryIdentityStorage | None =None) -> None:
        if storage is None:
            storage = InMemoryIdentityStorage()

        self._storage = storage
        self._items = storage.organization_users

    def add(self, organization_user: OrganizationUser) -> None:
        if organization_user.id in self._items:
            raise ValueError("OrganizationUser already exists")

        # unikalność (organization_id, user_id)
        if any(
            ou.organization_id == organization_user.organization_id
            and ou.user_id == organization_user.user_id
            for ou in self._items.values()
        ):
            raise ValueError("User already assigned to organization")

        self._items[organization_user.id] = organization_user

    def update(self, organization_user: OrganizationUser) -> None:
        if organization_user.id not in self._items:
            raise ValueError("OrganizationUser does not exist")
        self._items[organization_user.id] = organization_user

    def get(self, organization_user_id: UUID) -> OrganizationUser | None:
        return self._items.get(organization_user_id)

    def get_by_org_and_user(
        self,
        *,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationUser | None:
        for ou in self._items.values():
            if ou.organization_id == organization_id and ou.user_id == user_id:
                return ou
        return None

    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        active_only: bool = False,
    ) -> list[OrganizationUser]:
        result = [
            ou for ou in self._items.values()
            if ou.organization_id == organization_id
        ]
        if active_only:
            result = [ou for ou in result if ou.is_active]
        return result

    def list_by_user(
        self,
        user_id: UUID,
        *,
        active_only: bool = False,
    ) -> list[OrganizationUser]:
        result = [
            ou for ou in self._items.values()
            if ou.user_id == user_id
        ]
        if active_only:
            result = [ou for ou in result if ou.is_active]
        return result

    def exists(
        self,
        *,
        organization_id: UUID,
        user_id: UUID,
    ) -> bool:
        return any(
            ou.organization_id == organization_id and ou.user_id == user_id
            for ou in self._items.values()
        )

    def list_organizations_for_user(
            self,
            *,
            user_id: UUID,
            active_only: bool = True,
    ) -> list[OrganizationListItemDTO]:

        result: list[OrganizationListItemDTO] = []

        for membership in self._items.values():
            if membership.user_id != user_id:
                continue

            if active_only and not membership.is_active:
                continue

            organization = self._storage.organizations.get(membership.organization_id)
            if not organization:
                continue

            if active_only and not organization.is_active:
                continue

            result.append(
                OrganizationListItemDTO(
                    id=organization.id,
                    code=organization.code,
                    name=organization.name,
                    is_active=organization.is_active,
                    role=membership.role.value,
                )
            )

        return result

    def list_users_for_organization(
            self,
            *,
            organization_id: UUID,
            active_only: bool = False,
    ) -> list[OrganizationUserView]:

        result: list[OrganizationUserView] = []

        for membership in self._items.values():
            if membership.organization_id != organization_id:
                continue

            if active_only and not membership.is_active:
                continue

            user = self._storage.users.get(membership.user_id)
            if not user:
                continue  # defensywne

            result.append(
                OrganizationUserView(
                    user_id=user.id,
                    login=user.login,
                    full_name=user.full_name,
                    email=user.email,
                    role=membership.role,
                    is_active=membership.is_active,
                    invited_at=membership.invited_at,
                    accepted_at=membership.accepted_at,
                )
            )

        return result