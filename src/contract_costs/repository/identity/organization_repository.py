from abc import ABC, abstractmethod
from uuid import UUID

from contract_costs.model.identity.organization import Organization
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.model.identity.user import User


class OrganizationRepository(ABC):

    @abstractmethod
    def add_with_owner(
            self,
            *,
            organization: Organization,
            owner: User,
            membership: OrganizationUser,
    ) -> None:
        ...

    @abstractmethod
    def add(self, organization: Organization) -> None:
        ...

    @abstractmethod
    def update(self, organization: Organization) -> None:
        ...

    @abstractmethod
    def get(self, organization_id: UUID) -> Organization | None:
        ...

    @abstractmethod
    def get_by_code(self, code: str) -> Organization | None:
        ...

    @abstractmethod
    def list(self, *, active_only: bool = False) -> list[Organization]:
        ...

    @abstractmethod
    def exists(self, organization_id: UUID) -> bool:
        ...
