import pytest

from contract_costs.common.ids import new_uuid
from contract_costs.repository.inmemory.identity.organization_repository import (
    InMemoryOrganizationRepository,
)
from contract_costs.repository.inmemory.identity.user_repository import (
    InMemoryUserRepository,
)
from contract_costs.repository.mysql.identity.organization_repository import (
    MySqlOrganizationRepository,
)
from contract_costs.repository.mysql.identity.organization_user_repository import (
    MySqlOrganizationUserRepository,
)
from contract_costs.repository.mysql.identity.user_repository import (
    MySqlUserRepository,
)
from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.organization_user_builder import OrganizationUserBuilder
from tests.builders.user_builder import UserBuilder


def _bound_identity_repos_from_org_repo(organization_repo_contract):
    if organization_repo_contract.__class__.__name__.startswith("MySql"):
        conn = organization_repo_contract._connection
        return (
            MySqlOrganizationRepository(connection=conn),
            MySqlUserRepository(connection=conn),
            MySqlOrganizationUserRepository(connection=conn),
        )
    storage = getattr(organization_repo_contract, "_items", None)
    if storage is not None and hasattr(organization_repo_contract, "_users"):
        shared = type("Shared", (), {})()
        shared.organizations = organization_repo_contract._items
        shared.users = organization_repo_contract._users
        shared.organization_users = organization_repo_contract._memberships
        return (
            InMemoryOrganizationRepository(shared),
            InMemoryUserRepository(shared),
            None,
        )
    return organization_repo_contract, None, None


def _seed_org_user_for_org_user_repo(organization_user_repo_contract, org, user):
    if organization_user_repo_contract.__class__.__name__.startswith("MySql"):
        conn = organization_user_repo_contract._connection
        MySqlOrganizationRepository(connection=conn).add(org)
        MySqlUserRepository(connection=conn).add(user)
        return

    storage = organization_user_repo_contract._storage
    InMemoryOrganizationRepository(storage).add(org)
    InMemoryUserRepository(storage).add(user)


def test_organization_add_and_get(organization_repo_contract):
    org = OrganizationBuilder().with_code(f"ORG-{new_uuid().hex[:8]}").build()
    organization_repo_contract.add(org)

    loaded = organization_repo_contract.get(org.id)
    assert loaded is not None
    assert loaded.id == org.id
    assert loaded.code == org.code


def test_organization_get_by_code(organization_repo_contract):
    code = f"ORG-{new_uuid().hex[:8]}"
    org = OrganizationBuilder().with_code(code).build()
    organization_repo_contract.add(org)

    loaded = organization_repo_contract.get_by_code(code)
    assert loaded is not None
    assert loaded.id == org.id


def test_user_add_and_get(user_repo_contract):
    user = UserBuilder().with_login(f"user_{new_uuid().hex[:8]}").build()
    user_repo_contract.add(user)

    loaded = user_repo_contract.get(user.id)
    assert loaded is not None
    assert loaded.id == user.id
    assert loaded.login == user.login


def test_user_duplicate_login_raises(user_repo_contract):
    login = f"user_{new_uuid().hex[:8]}"
    u1 = UserBuilder().with_login(login).build()
    u2 = UserBuilder().with_login(login).build()
    user_repo_contract.add(u1)

    with pytest.raises(Exception):
        user_repo_contract.add(u2)


def test_organization_user_add_and_get(organization_user_repo_contract):
    membership = OrganizationUserBuilder().build()
    organization_user_repo_contract.add(membership)

    loaded = organization_user_repo_contract.get(membership.id)
    assert loaded is not None
    assert loaded.id == membership.id
    assert loaded.organization_id == membership.organization_id
    assert loaded.user_id == membership.user_id


def test_organization_user_unique_org_user_pair(organization_user_repo_contract):
    org_id = new_uuid()
    user_id = new_uuid()
    m1 = (
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_user_id(user_id)
        .build()
    )
    m2 = (
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_user_id(user_id)
        .build()
    )
    organization_user_repo_contract.add(m1)

    with pytest.raises(Exception):
        organization_user_repo_contract.add(m2)


def test_organization_user_list_by_organization_active_only(organization_user_repo_contract):
    org_id = new_uuid()
    active = (
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_is_active(True)
        .build()
    )
    inactive = (
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_is_active(False)
        .build()
    )
    organization_user_repo_contract.add(active)
    organization_user_repo_contract.add(inactive)

    listed = organization_user_repo_contract.list_by_organization(org_id, active_only=True)
    assert [m.id for m in listed] == [active.id]


def test_organization_update_list_exists(organization_repo_contract):
    org = OrganizationBuilder().with_code(f"ORG-{new_uuid().hex[:8]}").build()
    organization_repo_contract.add(org)

    org = OrganizationBuilder().with_id(org.id).with_code(org.code).with_name("Updated Org").build()
    organization_repo_contract.update(org)

    loaded = organization_repo_contract.get(org.id)
    assert loaded is not None
    assert loaded.name == "Updated Org"
    assert organization_repo_contract.exists(org.id) is True
    assert any(o.id == org.id for o in organization_repo_contract.list(active_only=False))


def test_organization_add_with_owner(organization_repo_contract, user_repo_contract, organization_user_repo_contract):
    org = OrganizationBuilder().with_code(f"ORG-{new_uuid().hex[:8]}").build()
    owner = UserBuilder().with_login(f"user_{new_uuid().hex[:8]}").build()
    membership = (
        OrganizationUserBuilder()
        .with_organization_id(org.id)
        .with_user_id(owner.id)
        .build()
    )

    organization_repo_contract.add_with_owner(
        organization=org,
        owner=owner,
        membership=membership,
    )

    assert organization_repo_contract.get(org.id) is not None
    if organization_repo_contract.__class__.__name__.startswith("MySql"):
        conn = organization_repo_contract._connection
        assert MySqlUserRepository(connection=conn).get(owner.id) is not None
        assert MySqlOrganizationUserRepository(connection=conn).get(membership.id) is not None
    else:
        assert owner.id in organization_repo_contract._users
        assert membership.id in organization_repo_contract._memberships


def test_user_get_by_login_update_list_exists(user_repo_contract):
    user = UserBuilder().with_login(f"user_{new_uuid().hex[:8]}").build()
    user_repo_contract.add(user)

    by_login = user_repo_contract.get_by_login(user.login)
    assert by_login is not None
    assert by_login.id == user.id
    assert user_repo_contract.exists(user.id) is True

    updated = (
        UserBuilder()
        .with_id(user.id)
        .with_login(user.login)
        .with_email(user.email)
        .with_is_active(user.is_active)
        .with_full_name("Updated Name")
        .build()
    )
    user_repo_contract.update(updated)
    assert user_repo_contract.get(user.id).full_name == "Updated Name"
    assert any(u.id == user.id for u in user_repo_contract.list(active_only=False))


def test_organization_user_update_get_by_org_user_list_by_user_exists(organization_user_repo_contract):
    org_id = new_uuid()
    user_id = new_uuid()
    membership = (
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_user_id(user_id)
        .with_is_active(True)
        .build()
    )
    organization_user_repo_contract.add(membership)

    membership = (
        OrganizationUserBuilder()
        .with_id(membership.id)
        .with_organization_id(org_id)
        .with_user_id(user_id)
        .with_is_active(False)
        .build()
    )
    organization_user_repo_contract.update(membership)

    by_pair = organization_user_repo_contract.get_by_org_and_user(
        organization_id=org_id,
        user_id=user_id,
    )
    assert by_pair is not None
    assert by_pair.is_active is False
    assert organization_user_repo_contract.exists(organization_id=org_id, user_id=user_id) is True
    assert [m.id for m in organization_user_repo_contract.list_by_user(user_id, active_only=False)] == [membership.id]


def test_organization_user_list_views(organization_repo_contract, user_repo_contract, organization_user_repo_contract):
    user = UserBuilder().with_login(f"user_{new_uuid().hex[:8]}").with_full_name("Jane User").build()
    org = OrganizationBuilder().with_code(f"ORG-{new_uuid().hex[:8]}").with_name("Org X").build()
    _seed_org_user_for_org_user_repo(organization_user_repo_contract, org, user)
    membership = (
        OrganizationUserBuilder()
        .with_organization_id(org.id)
        .with_user_id(user.id)
        .with_is_active(True)
        .build()
    )
    organization_user_repo_contract.add(membership)

    orgs = organization_user_repo_contract.list_organizations_for_user(
        user_id=user.id,
        active_only=True,
    )
    users = organization_user_repo_contract.list_users_for_organization(
        organization_id=org.id,
        active_only=True,
    )

    assert len(orgs) == 1
    assert orgs[0].id == org.id
    assert len(users) == 1
    assert users[0].user_id == user.id
