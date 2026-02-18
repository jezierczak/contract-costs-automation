from uuid import uuid4

import pytest

from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.services.identity.accept.accept_organization_invite_service import AcceptOrganizationInviteService
from contract_costs.services.identity.accept.dto.accept_organization_invite_command import AcceptOrganizationInviteCommand
from contract_costs.services.identity.add.add_organization_user_service import AddOrganizationUserService
from contract_costs.services.identity.add.create_user_service import CreateUserService
from contract_costs.services.identity.add.dto.assign_user_to_organization_command import AssignUserToOrganizationCommand
from contract_costs.services.identity.add.dto.create_user_command import CreateUserCommand
from contract_costs.services.identity.change.change_organization_user_role_service import ChangeOrganizationUserRoleService
from contract_costs.services.identity.change.dto.change_organization_user_role_command import ChangeOrganizationUserRoleCommand
from contract_costs.services.identity.deactivate.deactivate_organization_user_service import DeactivateOrganizationUserService
from contract_costs.services.identity.deactivate.dto.deactivate_organization_user_command import DeactivateOrganizationUserCommand
from contract_costs.services.identity.exceptions import PermissionDenied
from contract_costs.services.identity.remove.dto.remove_organization_user_command import RemoveOrganizationUserCommand
from contract_costs.services.identity.remove.remove_organization_user_service import RemoveOrganizationUserService
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork
from tests.unit.services.identity.helpers import make_membership, make_org, make_user


def test_add_org_user_and_accept_invite_with_uow():
    uow = InMemoryUnitOfWork()
    org_id = make_org(uow.organizations)
    owner_id = make_user(uow.users, login="owner")
    target_user_id = make_user(uow.users, login="target")
    make_membership(
        uow.organization_users,
        organization_id=org_id,
        user_id=owner_id,
        role=OrganizationRole.OWNER,
    )

    add_service = AddOrganizationUserService()
    add_service.execute(
        action=AssignUserToOrganizationCommand(
            organization_id=org_id,
            actor_user_id=owner_id,
            target_user_id=target_user_id,
            role=OrganizationRole.USER,
        ),
        uow=uow,
    )

    membership = uow.organization_users.get_by_org_and_user(organization_id=org_id, user_id=target_user_id)
    assert membership is not None

    accept_service = AcceptOrganizationInviteService()
    accept_service.execute(
        action=AcceptOrganizationInviteCommand(
            organization_id=org_id,
            actor_user_id=target_user_id,
        ),
        uow=uow,
    )


def test_create_user_and_membership_management_services_use_uow():
    uow = InMemoryUnitOfWork()
    org_id = make_org(uow.organizations)
    owner_id = make_user(uow.users, login="owner")
    target_id = make_user(uow.users, login="target")

    make_membership(
        uow.organization_users,
        organization_id=org_id,
        user_id=owner_id,
        role=OrganizationRole.OWNER,
    )
    make_membership(
        uow.organization_users,
        organization_id=org_id,
        user_id=target_id,
        role=OrganizationRole.USER,
    )

    create_user_id = CreateUserService().execute(
        action=CreateUserCommand(
            organization_id=org_id,
            actor_user_id=owner_id,
            login="new-user",
            email=None,
            full_name=None,
        ),
        uow=uow,
    )
    assert uow.users.get(create_user_id) is not None

    ChangeOrganizationUserRoleService().execute(
        action=ChangeOrganizationUserRoleCommand(
            organization_id=org_id,
            actor_user_id=owner_id,
            target_user_id=target_id,
            new_role=OrganizationRole.ADMIN,
        ),
        uow=uow,
    )

    DeactivateOrganizationUserService().execute(
        action=DeactivateOrganizationUserCommand(
            organization_id=org_id,
            actor_user_id=owner_id,
            target_user_id=target_id,
        ),
        uow=uow,
    )

    RemoveOrganizationUserService().execute(
        action=RemoveOrganizationUserCommand(
            organization_id=org_id,
            actor_user_id=owner_id,
            target_user_id=target_id,
        ),
        uow=uow,
    )


def test_add_org_user_requires_actor_membership():
    uow = InMemoryUnitOfWork()
    org_id = make_org(uow.organizations)
    actor_id = make_user(uow.users, login="actor")
    target_id = make_user(uow.users, login="target")

    with pytest.raises(PermissionDenied):
        AddOrganizationUserService().execute(
            action=AssignUserToOrganizationCommand(
                organization_id=org_id,
                actor_user_id=actor_id,
                target_user_id=target_id,
                role=OrganizationRole.USER,
            ),
            uow=uow,
        )
