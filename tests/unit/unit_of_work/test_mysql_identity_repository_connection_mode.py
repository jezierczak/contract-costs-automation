from contract_costs.repository.inmemory.identity.in_memory_storage_repository import (
    InMemoryIdentityStorage,
)
from contract_costs.repository.inmemory.identity.organization_repository import (
    InMemoryOrganizationRepository,
)
from contract_costs.repository.inmemory.identity.organization_user_repository import (
    InMemoryOrganizationUserRepository,
)
from contract_costs.repository.inmemory.identity.user_repository import InMemoryUserRepository
from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.organization_user_builder import OrganizationUserBuilder
from tests.builders.user_builder import UserBuilder


def test_inmemory_identity_repos_share_state_when_using_same_storage():
    storage = InMemoryIdentityStorage()
    org_repo = InMemoryOrganizationRepository(storage)
    user_repo = InMemoryUserRepository(storage)
    membership_repo = InMemoryOrganizationUserRepository(storage)

    organization = OrganizationBuilder().build()
    user = UserBuilder().build()
    membership = (
        OrganizationUserBuilder()
        .with_organization_id(organization.id)
        .with_user_id(user.id)
        .build()
    )

    org_repo.add(organization)
    user_repo.add(user)
    membership_repo.add(membership)

    assert org_repo.get(organization.id) == organization
    assert user_repo.get(user.id) == user
    assert membership_repo.get(membership.id) == membership


def test_inmemory_identity_repo_add_with_owner_persists_all_entities():
    storage = InMemoryIdentityStorage()
    org_repo = InMemoryOrganizationRepository(storage)
    user_repo = InMemoryUserRepository(storage)
    membership_repo = InMemoryOrganizationUserRepository(storage)

    organization = OrganizationBuilder().build()
    owner = UserBuilder().build()
    membership = (
        OrganizationUserBuilder()
        .with_organization_id(organization.id)
        .with_user_id(owner.id)
        .build()
    )

    org_repo.add_with_owner(
        organization=organization,
        owner=owner,
        membership=membership,
    )

    assert org_repo.get(organization.id) == organization
    assert user_repo.get(owner.id) == owner
    assert membership_repo.get_by_org_and_user(
        organization_id=organization.id,
        user_id=owner.id,
    ) == membership
