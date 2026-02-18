
from unittest.mock import MagicMock

from contract_costs.model.identity.organization_role import OrganizationRole
from contract_costs.services.identity.add.create_organization_with_owner import CreateOrganizationWithOwnerService
from contract_costs.services.identity.add.dto.create_organization_command import CreateOrganizationCommand


class _FakeUow:
    def __init__(self, *, organization_repo, user_repo, organization_user_repo):
        self.organizations = organization_repo
        self.users = user_repo
        self.organization_users = organization_user_repo
        self._hooks = []

    def add_post_commit_hook(self, hook):
        self._hooks.append(hook)


def test_create_organization_with_owner(organization_repo, user_repo, organization_user_repo) -> None:

    service = CreateOrganizationWithOwnerService(
        init_app_service=MagicMock(),
    )

    cmd = CreateOrganizationCommand(
        organization_code="REMONTIVO",
        organization_name="Remontivo Sp. z o.o.",
        owner_login="jarek",
        owner_email="jarek@remontivo.pl",
        owner_full_name="Jarosław Kowalski",
        created_by_user_id=None,
    )

    org_id = service.execute(
        action=cmd,
        uow=_FakeUow(
            organization_repo=organization_repo,
            user_repo=user_repo,
            organization_user_repo=organization_user_repo,
        ),
    )

    # --- ASSERTS ---
    org = organization_repo.get(org_id)
    assert org is not None
    assert org.code == "REMONTIVO"
    assert org.is_active is True

    user = user_repo.get_by_login("jarek")
    assert user is not None
    assert user.is_active is True

    membership = organization_user_repo.get_by_org_and_user(
        organization_id=org.id,
        user_id=user.id,
    )

    assert membership is not None
    assert membership.role == OrganizationRole.OWNER
    assert membership.is_active is True
