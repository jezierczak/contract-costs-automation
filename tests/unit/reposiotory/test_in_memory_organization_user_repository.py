import pytest

from contract_costs.common.ids import new_uuid
from tests.builders.organization_builder import OrganizationBuilder
from tests.builders.organization_user_builder import OrganizationUserBuilder
from tests.builders.user_builder import UserBuilder


def test_add_and_get_membership(organization_user_repo):
    membership = OrganizationUserBuilder().build()

    organization_user_repo.add(membership)

    assert organization_user_repo.get(membership.id) == membership


def test_duplicate_membership_id_raises(organization_user_repo):
    membership = OrganizationUserBuilder().build()

    organization_user_repo.add(membership)

    with pytest.raises(ValueError):
        organization_user_repo.add(membership)

def test_same_user_cannot_be_assigned_twice(organization_user_repo):
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

    organization_user_repo.add(m1)

    with pytest.raises(ValueError):
        organization_user_repo.add(m2)


def test_list_by_organization_active_only(organization_user_repo):
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

    organization_user_repo.add(active)
    organization_user_repo.add(inactive)

    result = organization_user_repo.list_by_organization(
        org_id,
        active_only=True,
    )

    assert result == [active]


def test_update_membership(organization_user_repo):
    membership = OrganizationUserBuilder().with_is_active(True).build()
    organization_user_repo.add(membership)

    membership = OrganizationUserBuilder().with_id(membership.id).with_organization_id(membership.organization_id).with_user_id(membership.user_id).with_is_active(False).build()
    organization_user_repo.update(membership)

    loaded = organization_user_repo.get(membership.id)
    assert loaded is not None
    assert loaded.is_active is False


def test_update_missing_membership_raises(organization_user_repo):
    with pytest.raises(ValueError):
        organization_user_repo.update(OrganizationUserBuilder().build())


def test_get_by_org_and_user_and_exists(organization_user_repo):
    org_id = new_uuid()
    user_id = new_uuid()
    membership = (
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_user_id(user_id)
        .build()
    )
    organization_user_repo.add(membership)

    loaded = organization_user_repo.get_by_org_and_user(
        organization_id=org_id,
        user_id=user_id,
    )
    assert loaded == membership
    assert organization_user_repo.exists(organization_id=org_id, user_id=user_id) is True
    assert organization_user_repo.exists(organization_id=org_id, user_id=new_uuid()) is False


def test_list_by_user_active_only(organization_user_repo):
    user_id = new_uuid()
    active = OrganizationUserBuilder().with_user_id(user_id).with_is_active(True).build()
    inactive = OrganizationUserBuilder().with_user_id(user_id).with_is_active(False).build()
    organization_user_repo.add(active)
    organization_user_repo.add(inactive)

    listed = organization_user_repo.list_by_user(user_id, active_only=True)
    assert listed == [active]


def test_list_organizations_for_user_filters_by_membership_and_org_status(
    organization_repo,
    user_repo,
    organization_user_repo,
):
    user = UserBuilder().build()
    user_repo.add(user)
    active_org = OrganizationBuilder().with_is_active(True).with_code("ORG-A").build()
    inactive_org = OrganizationBuilder().with_is_active(False).with_code("ORG-I").build()
    organization_repo.add(active_org)
    organization_repo.add(inactive_org)

    active_membership = (
        OrganizationUserBuilder()
        .with_user_id(user.id)
        .with_organization_id(active_org.id)
        .with_is_active(True)
        .build()
    )
    inactive_membership = (
        OrganizationUserBuilder()
        .with_user_id(user.id)
        .with_organization_id(inactive_org.id)
        .with_is_active(False)
        .build()
    )
    organization_user_repo.add(active_membership)
    organization_user_repo.add(inactive_membership)

    active_only = organization_user_repo.list_organizations_for_user(
        user_id=user.id,
        active_only=True,
    )
    all_items = organization_user_repo.list_organizations_for_user(
        user_id=user.id,
        active_only=False,
    )

    assert [x.id for x in active_only] == [active_org.id]
    assert {x.id for x in all_items} == {active_org.id, inactive_org.id}


def test_list_users_for_organization_skips_missing_user_and_filters_active(
    organization_user_repo,
    user_repo,
):
    org_id = new_uuid()
    user_active = UserBuilder().with_login("jane").build()
    user_inactive = UserBuilder().with_login("john").build()
    user_repo.add(user_active)
    user_repo.add(user_inactive)

    active_membership = (
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_user_id(user_active.id)
        .with_is_active(True)
        .build()
    )
    missing_user_membership = (
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_user_id(new_uuid())
        .with_is_active(True)
        .build()
    )
    inactive_membership = (
        OrganizationUserBuilder()
        .with_organization_id(org_id)
        .with_user_id(user_inactive.id)
        .with_is_active(False)
        .with_id(new_uuid())
        .build()
    )
    organization_user_repo.add(active_membership)
    organization_user_repo.add(missing_user_membership)
    organization_user_repo.add(inactive_membership)

    active_only = organization_user_repo.list_users_for_organization(
        organization_id=org_id,
        active_only=True,
    )
    all_items = organization_user_repo.list_users_for_organization(
        organization_id=org_id,
        active_only=False,
    )

    assert len(active_only) == 1
    assert active_only[0].login == "jane"
    assert len(all_items) == 2
