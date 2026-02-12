import pytest
from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.organization_user_builder import OrganizationUserBuilder
from tests.builders.user_builder import UserBuilder


def test_add_with_owner_creates_all(
    organization_repo,
    user_repo,
    organization_user_repo,
):
    org = OrganizationBuilder().build()
    owner = UserBuilder().build()
    membership = (OrganizationUserBuilder()
                  .with_organization_id(org.id)
                  .with_user_id(owner.id)
                  .build())

    organization_repo.add_with_owner(org, owner, membership)

    assert organization_repo.get(org.id) == org
    assert user_repo.get(owner.id) == owner
    assert organization_user_repo.get(membership.id) == membership

def test_add_duplicate_organization_raises(organization_repo):
    org = OrganizationBuilder().build()

    organization_repo.add(org)

    with pytest.raises(ValueError):
        organization_repo.add(org)

def test_get_by_code(organization_repo):
    org = OrganizationBuilder().with_code("ABC").build()

    organization_repo.add(org)

    assert organization_repo.get_by_code("ABC") == org


def test_list_active_only(organization_repo):
    active = OrganizationBuilder().with_is_active(True).build()
    inactive = OrganizationBuilder().with_is_active(False).build()

    organization_repo.add(active)
    organization_repo.add(inactive)

    result = organization_repo.list_contracts(active_only=True)

    assert result == [active]
