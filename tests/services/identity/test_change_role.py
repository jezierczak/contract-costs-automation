import pytest

from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.services.identity.change.change_organization_user_role_service import \
    ChangeOrganizationUserRoleService
from contract_costs.services.identity.change.dto.change_organization_user_role_command import \
    ChangeOrganizationUserRoleCommand
from contract_costs.services.identity.exceptions import PermissionDenied
from .helpers import make_org_with_owner


def test_owner_cannot_change_own_role(org_repo, user_repo, org_user_repo):
    org_id, owner_id = make_org_with_owner(org_repo, user_repo, org_user_repo)

    cmd = ChangeOrganizationUserRoleCommand(
        organization_id=org_id,
        actor_user_id=owner_id,
        target_user_id=owner_id,
        new_role=OrganizationRole.ADMIN,
    )

    service = ChangeOrganizationUserRoleService(
        organization_user_repo=org_user_repo
    )

    with pytest.raises(PermissionDenied):
        service.execute(cmd)
