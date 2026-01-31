from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.model.identity.organization_user import OrganizationUser


class OrganizationUserRepository(ABC):

    @abstractmethod
    def add(self, organization_user: OrganizationUser) -> None:
        ...

    @abstractmethod
    def update(self, organization_user: OrganizationUser) -> None:
        ...

    @abstractmethod
    def get(self, organization_user_id: UUID) -> OrganizationUser | None:
        ...

    @abstractmethod
    def get_by_org_and_user(
        self,
        *,
        organization_id: UUID,
        user_id: UUID,
    ) -> OrganizationUser | None:
        ...

    @abstractmethod
    def list_by_organization(
        self,
        organization_id: UUID,
        *,
        active_only: bool = False,
    ) -> list[OrganizationUser]:
        ...

    @abstractmethod
    def list_by_user(
        self,
        user_id: UUID,
        *,
        active_only: bool = False,
    ) -> list[OrganizationUser]:
        ...

    @abstractmethod
    def exists(
        self,
        *,
        organization_id: UUID,
        user_id: UUID,
    ) -> bool:
        ...
