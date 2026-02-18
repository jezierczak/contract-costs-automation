from contract_costs.repository.factory.repository_factory import RepoBackend, RepositoryFactory
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.organization_user_builder import OrganizationUserBuilder
from tests.builders.user_builder import UserBuilder


def test_factory_creates_in_memory_uow():
    factory = RepositoryFactory(RepoBackend.MEMORY)

    uow = factory.unit_of_work()

    assert isinstance(uow, InMemoryUnitOfWork)

def test_in_memory_uow_shares_identity_state_between_repositories():
    uow = InMemoryUnitOfWork()
    organization = OrganizationBuilder().build()
    user = UserBuilder().build()
    membership = (
        OrganizationUserBuilder()
        .with_organization_id(organization.id)
        .with_user_id(user.id)
        .build()
    )

    uow.organizations.add_with_owner(
        organization=organization,
        owner=user,
        membership=membership,
    )

    assert uow.organizations.get(organization.id) == organization
    assert uow.users.get(user.id) == user
    assert uow.organization_users.get(membership.id) == membership
