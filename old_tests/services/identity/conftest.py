import pytest

from contract_costs.repository.identity.organization_repository import OrganizationRepository
from contract_costs.repository.identity.organization_user_repository import OrganizationUserRepository
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.repository.inmemory.identity.in_memory_storage_repository import InMemoryIdentityStorage
from contract_costs.repository.inmemory.identity.organization_repository import InMemoryOrganizationRepository
from contract_costs.repository.inmemory.identity.organization_user_repository import InMemoryOrganizationUserRepository
from contract_costs.repository.inmemory.identity.user_repository import InMemoryUserRepository


@pytest.fixture
def identity_storage():
    return InMemoryIdentityStorage()

@pytest.fixture
def org_repo(identity_storage):
    return InMemoryOrganizationRepository(identity_storage)

@pytest.fixture
def user_repo(identity_storage):
    return InMemoryUserRepository(identity_storage)

@pytest.fixture
def org_user_repo(identity_storage):
    return InMemoryOrganizationUserRepository(identity_storage)