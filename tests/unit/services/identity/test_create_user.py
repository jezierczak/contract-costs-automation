import pytest
from uuid import uuid4

from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.repository.identity.user_repository import UserRepository
from contract_costs.services.identity.add.add_organization_user_service import AddOrganizationUserService
from contract_costs.services.identity.add.create_user_service import CreateUserService
from contract_costs.services.identity.add.dto.assign_user_to_organization_command import AssignUserToOrganizationCommand
from contract_costs.services.identity.add.dto.create_user_command import CreateUserCommand
from contract_costs.services.identity.change.change_organization_user_role_service import \
    ChangeOrganizationUserRoleService
from contract_costs.services.identity.change.dto.change_organization_user_role_command import \
    ChangeOrganizationUserRoleCommand
from contract_costs.services.identity.deactivate.deactivate_organization_user_service import \
    DeactivateOrganizationUserService
from contract_costs.services.identity.deactivate.dto.deactivate_organization_user_command import \
    DeactivateOrganizationUserCommand
from contract_costs.services.identity.exceptions import UserAlreadyExists, PermissionDenied
from contract_costs.services.identity.remove.dto.remove_organization_user_command import RemoveOrganizationUserCommand
from contract_costs.services.identity.remove.remove_organization_user_service import RemoveOrganizationUserService
from .helpers import (
    make_org_with_users,
    make_org_with_owner,
    make_org_owner_user,
    make_org_owner_admin,
    make_org,
    make_user,
    make_membership,
)


class _FakeUow:
    def __init__(self, *, organization_repo=None, user_repo=None, organization_user_repo=None):
        self.organizations = organization_repo
        self.users = user_repo
        self.organization_users = organization_user_repo


def test_create_user_success(user_repo:UserRepository):
    service = CreateUserService()
    uow = _FakeUow(user_repo=user_repo)

    cmd = CreateUserCommand(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        login="jarek",
        email="jarek@test.pl",
        full_name="Jarek Test",
    )

    user_id = service.execute(action=cmd, uow=uow)

    user = user_repo.get(user_id)
    assert user.login == "jarek"
    assert user.is_active is True

def test_create_user_duplicate_login(user_repo):
    service = CreateUserService()
    uow = _FakeUow(user_repo=user_repo)

    make_user(user_repo, login="jarek", is_active=True)

    cmd = CreateUserCommand(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        login="jarek",
        email=None,
        full_name=None,
    )

    with pytest.raises(UserAlreadyExists):
        service.execute(action=cmd, uow=uow)

def test_add_user_actor_not_member(
    organization_repo, user_repo, organization_user_repo
):
    service = AddOrganizationUserService()
    uow = _FakeUow(
        organization_repo=organization_repo,
        user_repo=user_repo,
        organization_user_repo=organization_user_repo,
    )

    cmd = AssignUserToOrganizationCommand(
        organization_id=make_org(organization_repo),
        actor_user_id=make_user(user_repo),
        target_user_id=make_user(user_repo),
        role=OrganizationRole.USER,
    )

    with pytest.raises(PermissionDenied):
        service.execute(action=cmd, uow=uow)

def test_add_user_actor_not_admin(
    organization_repo, user_repo, organization_user_repo
):
    org_id = make_org(organization_repo)
    actor_id = make_user(user_repo)
    target_id = make_user(user_repo)

    make_membership(
        organization_user_repo,
        organization_id=org_id,
        user_id=actor_id,
        role=OrganizationRole.USER,
        is_active=True,
    )

    service = AddOrganizationUserService()
    uow = _FakeUow(
        organization_repo=organization_repo,
        user_repo=user_repo,
        organization_user_repo=organization_user_repo,
    )

    cmd = AssignUserToOrganizationCommand(
        organization_id=org_id,
        actor_user_id=actor_id,
        target_user_id=target_id,
        role=OrganizationRole.USER,
    )

    membership_id = service.execute(action=cmd, uow=uow)
    membership = organization_user_repo.get(membership_id)
    assert membership is not None
    assert membership.user_id == target_id


def test_add_user_success(
        organization_repo, user_repo, organization_user_repo
):
    org_id = make_org(organization_repo)
    owner_id = make_user(user_repo)
    target_id = make_user(user_repo)

    make_membership(
        organization_user_repo,
        organization_id=org_id,
        user_id=owner_id,
        role=OrganizationRole.OWNER,
        is_active=True,
    )

    service = AddOrganizationUserService()
    uow = _FakeUow(
        organization_repo=organization_repo,
        user_repo=user_repo,
        organization_user_repo=organization_user_repo,
    )

    cmd = AssignUserToOrganizationCommand(
        organization_id=org_id,
        actor_user_id=owner_id,
        target_user_id=target_id,
        role=OrganizationRole.USER,
    )

    membership_id = service.execute(action=cmd, uow=uow)

    membership = organization_user_repo.get(membership_id)
    assert membership.role == OrganizationRole.USER
    assert membership.is_active is True


def test_remove_owner_forbidden(   organization_repo, user_repo, organization_user_repo):
    org_id, owner_id = make_org_with_owner(organization_repo,user_repo,organization_user_repo)

    cmd = RemoveOrganizationUserCommand(
        organization_id=org_id,
        actor_user_id=owner_id,
        target_user_id=owner_id,
    )

    service = RemoveOrganizationUserService()

    with pytest.raises(PermissionDenied):
        service.execute(
            action=cmd,
            uow=_FakeUow(organization_user_repo=organization_user_repo),
        )
def test_remove_user_success(   organization_repo, user_repo, organization_user_repo):
    org_id, owner_id, admin_id, user_id = make_org_with_users(organization_repo,user_repo,organization_user_repo)

    cmd = RemoveOrganizationUserCommand(
        organization_id=org_id,
        actor_user_id=admin_id,
        target_user_id=user_id,
    )

    service = RemoveOrganizationUserService()

    service.execute(
        action=cmd,
        uow=_FakeUow(organization_user_repo=organization_user_repo),
    )

    membership = organization_user_repo.get_by_org_and_user(
        organization_id=org_id,
        user_id=user_id,
    )

    assert membership.is_active is False



def test_admin_cannot_change_owner(   organization_repo, user_repo, organization_user_repo):
    org_id, owner_id, admin_id = make_org_owner_admin(
        organization_repo, user_repo, organization_user_repo
    )

    cmd = ChangeOrganizationUserRoleCommand(
        organization_id=org_id,
        actor_user_id=admin_id,
        target_user_id=owner_id,
        new_role=OrganizationRole.USER,
    )

    service = ChangeOrganizationUserRoleService()

    with pytest.raises(PermissionDenied):
        service.execute(
            action=cmd,
            uow=_FakeUow(organization_user_repo=organization_user_repo),
        )


def test_owner_promotes_user(   organization_repo, user_repo, organization_user_repo):
    org_id, owner_id, user_id = make_org_owner_user(organization_repo,user_repo,organization_user_repo)

    cmd = ChangeOrganizationUserRoleCommand(
        organization_id=org_id,
        actor_user_id=owner_id,
        target_user_id=user_id,
        new_role=OrganizationRole.ADMIN,
    )

    service = ChangeOrganizationUserRoleService()

    service.execute(
        action=cmd,
        uow=_FakeUow(organization_user_repo=organization_user_repo),
    )

    membership = organization_user_repo.get_by_org_and_user(
        organization_id=org_id,
        user_id=user_id,
    )

    assert membership.role == OrganizationRole.ADMIN

def test_deactivate_owner_forbidden(   organization_repo, user_repo, organization_user_repo):
    org_id, owner_id = make_org_with_owner(org_repo=organization_repo,user_repo=user_repo,org_user_repo=organization_user_repo)

    cmd = DeactivateOrganizationUserCommand(
        organization_id=org_id,
        actor_user_id=owner_id,
        target_user_id=owner_id,
    )

    service = DeactivateOrganizationUserService()

    with pytest.raises(PermissionDenied):
        service.execute(
            action=cmd,
            uow=_FakeUow(organization_user_repo=organization_user_repo),
        )

def test_deactivate_user_success(   organization_repo, user_repo, organization_user_repo):
    org_id, owner_id, admin_id, user_id = make_org_with_users(org_repo=organization_repo,user_repo=user_repo,org_user_repo=organization_user_repo)

    cmd = DeactivateOrganizationUserCommand(
        organization_id=org_id,
        actor_user_id=admin_id,
        target_user_id=user_id,
    )

    service = DeactivateOrganizationUserService()

    service.execute(
        action=cmd,
        uow=_FakeUow(organization_user_repo=organization_user_repo),
    )

    membership = organization_user_repo.get_by_org_and_user(
        organization_id=org_id,
        user_id=user_id,
    )

    assert membership.is_active is False
