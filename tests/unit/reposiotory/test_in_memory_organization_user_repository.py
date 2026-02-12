import pytest

from contract_costs.common.ids import new_uuid
from tests.builders.organization_user_builder import OrganizationUserBuilder


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
