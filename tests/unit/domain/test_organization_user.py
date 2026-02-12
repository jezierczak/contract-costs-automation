import pytest
from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now

from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.model.identity.organization_role import OrganizationRole


def build_org_user(
    *,
    role:OrganizationRole = OrganizationRole.USER,
    is_active=True,
):
    return OrganizationUser(
        id=new_uuid(),
        organization_id=new_uuid(),
        user_id=new_uuid(),
        role=role,
        is_active=is_active,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        invited_at=None,
        invited_by_user_id=None,
        accepted_at=None,
    )


def test_organization_user_creation():
    org_user = build_org_user()

    assert org_user.role == OrganizationRole.USER
    assert org_user.is_active is True
    assert org_user.updated_at is None
    assert org_user.invited_at is None




def test_organization_user_is_immutable():
    org_user = build_org_user()

    with pytest.raises(Exception):
        org_user.role = OrganizationRole.ADMIN


def test_organization_user_with_admin_role():
    org_user = build_org_user(role=OrganizationRole.ADMIN)

    assert org_user.role == OrganizationRole.ADMIN


def test_organization_user_equality():
    now = utc_now()
    user_id = new_uuid()
    org_id = new_uuid()
    id_ = new_uuid()

    u1 = OrganizationUser(
        id=id_,
        organization_id=org_id,
        user_id=user_id,
        role=OrganizationRole.USER,
        is_active=True,
        created_at=now,
        created_by_user_id=None,
    )

    u2 = OrganizationUser(
        id=id_,
        organization_id=org_id,
        user_id=user_id,
        role=OrganizationRole.USER,
        is_active=True,
        created_at=now,
        created_by_user_id=None,
    )

    assert u1 == u2
