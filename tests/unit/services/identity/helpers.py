from datetime import datetime
from uuid import UUID

from contract_costs.common.ids import new_uuid
from contract_costs.common.time import utc_now
from contract_costs.model.identity.organization import Organization
from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.model.identity.organization_user import OrganizationUser
from contract_costs.model.identity.user import User

def make_user(
    user_repo,
    *,
    login: str | None = None,
    is_active: bool = True,
) -> UUID:
    user = User(
        id=new_uuid(),
        login=login or f"user-{new_uuid().hex[:6]}",
        email=None,
        full_name=None,
        is_active=is_active,
        created_at=utc_now(),
        created_by_user_id=None,
    )
    user_repo.add(user)
    return user.id

def make_org(
    org_repo,
    *,
    code: str | None = None,
    name: str | None = None,
) -> UUID:
    org = Organization(
        id=new_uuid(),
        code=code or f"ORG-{new_uuid().hex[:6]}",
        name=name or "Test org",
        is_active=True,
        created_at=utc_now(),
        created_by_user_id=None,
        updated_at=None,
        updated_by_user_id=None,
        settings=None,
    )
    org_repo.add(org)
    return org.id

def make_membership(
    org_user_repo,
    *,
    organization_id: UUID,
    user_id: UUID,
    role: OrganizationRole,
    is_active: bool = True,
) -> UUID:
    membership = OrganizationUser(
        id=new_uuid(),
        organization_id=organization_id,
        user_id=user_id,
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
    org_user_repo.add(membership)
    return membership.id

def make_org_with_owner(org_repo, user_repo, org_user_repo):
    org_id = make_org(org_repo)
    owner_id = make_user(user_repo, login="owner")

    make_membership(
        org_user_repo,
        organization_id=org_id,
        user_id=owner_id,
        role=OrganizationRole.OWNER,
    )

    return org_id, owner_id

def make_org_with_users(org_repo, user_repo, org_user_repo):
    org_id = make_org(org_repo)

    owner_id = make_user(user_repo, login="owner")
    admin_id = make_user(user_repo, login="admin")
    user_id = make_user(user_repo, login="user")

    make_membership(
        org_user_repo,
        organization_id=org_id,
        user_id=owner_id,
        role=OrganizationRole.OWNER,
    )
    make_membership(
        org_user_repo,
        organization_id=org_id,
        user_id=admin_id,
        role=OrganizationRole.ADMIN,
    )
    make_membership(
        org_user_repo,
        organization_id=org_id,
        user_id=user_id,
        role=OrganizationRole.USER,
    )

    return org_id, owner_id, admin_id, user_id

def make_org_owner_user(org_repo, user_repo, org_user_repo):
    org_id = make_org(org_repo)

    owner_id = make_user(user_repo, login="owner")
    user_id = make_user(user_repo, login="user")

    make_membership(
        org_user_repo,
        organization_id=org_id,
        user_id=owner_id,
        role=OrganizationRole.OWNER,
    )
    make_membership(
        org_user_repo,
        organization_id=org_id,
        user_id=user_id,
        role=OrganizationRole.USER,
    )

    return org_id, owner_id, user_id

def make_org_owner_admin(org_repo, user_repo, org_user_repo):
    org_id = make_org(org_repo)

    owner_id = make_user(user_repo, login="owner")
    admin_id = make_user(user_repo, login="admin")

    make_membership(
        org_user_repo,
        organization_id=org_id,
        user_id=owner_id,
        role=OrganizationRole.OWNER,
    )

    make_membership(
        org_user_repo,
        organization_id=org_id,
        user_id=admin_id,
        role=OrganizationRole.ADMIN,
    )

    return org_id, owner_id, admin_id
