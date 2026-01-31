from uuid import UUID

from contract_costs.model.identity.organization import Organization
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.model.identity.user import User
from contract_costs.repository.identity.organization_repository import OrganizationRepository
from contract_costs.repository.inmemory.identity.in_memory_storage_repository import InMemoryIdentityStorage


class InMemoryOrganizationRepository(OrganizationRepository):

    def __init__(self, storage: InMemoryIdentityStorage | None =None) -> None:
        if not storage:
            self._items: dict[UUID, Organization] = {}
            self._users: dict[UUID, User] = {}
            self._memberships: dict[UUID, OrganizationUser] = {}
        else:
            self._items= storage.organizations
            self._users=storage.users
            self._memberships =storage.organization_users

    def add_with_owner(
        self,
        organization: Organization,
        owner: User,
        membership: OrganizationUser,
    ) -> None:
        # „transakcja” in-memory = zwykłe dodanie
        self._items[organization.id] = organization
        self._users[owner.id] = owner
        self._memberships[membership.id] = membership

    def add(self, organization: Organization) -> None:
        if organization.id in self._items:
            raise ValueError("Organization already exists")
        self._items[organization.id] = organization

    def update(self, organization: Organization) -> None:
        if organization.id not in self._items:
            raise ValueError("Organization does not exist")
        self._items[organization.id] = organization

    def get(self, organization_id: UUID) -> Organization | None:
        return self._items.get(organization_id)

    def get_by_code(self, code: str) -> Organization | None:
        for org in self._items.values():
            if org.code == code:
                return org
        return None

    def list(self, *, active_only: bool = False) -> list[Organization]:
        if not active_only:
            return list(self._items.values())
        return [o for o in self._items.values() if o.is_active]

    def exists(self, organization_id: UUID) -> bool:
        return organization_id in self._items
