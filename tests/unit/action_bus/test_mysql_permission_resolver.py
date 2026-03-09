from types import SimpleNamespace
from uuid import uuid4

from contract_costs.action_bus.action_type import ActionType
from contract_costs.action_bus.permission_resolver import MySqlPermissionResolver
from contract_costs.model.identity.organization_role import OrganizationRole


class _OrgUserRepoStub:
    def __init__(self, membership):
        self.membership = membership
        self.calls = []

    def get_by_org_and_user(self, *, organization_id, user_id):
        self.calls.append((organization_id, user_id))
        return self.membership


def _membership(*, role, is_active=True):
    return SimpleNamespace(role=role, is_active=is_active)


def test_resolver_returns_false_when_membership_missing():
    repo = _OrgUserRepoStub(membership=None)
    resolver = MySqlPermissionResolver(org_user_repo=repo)

    allowed = resolver.has_permission(
        organization_id=uuid4(),
        user_id=uuid4(),
        action_type=ActionType.CONTRACT_MANAGEMENT,
    )

    assert allowed is False


def test_resolver_returns_false_when_membership_inactive():
    repo = _OrgUserRepoStub(
        membership=_membership(role=OrganizationRole.ADMIN, is_active=False)
    )
    resolver = MySqlPermissionResolver(org_user_repo=repo)

    allowed = resolver.has_permission(
        organization_id=uuid4(),
        user_id=uuid4(),
        action_type=ActionType.CONTRACT_MANAGEMENT,
    )

    assert allowed is False


def test_resolver_owner_always_allowed():
    repo = _OrgUserRepoStub(
        membership=_membership(role=OrganizationRole.OWNER, is_active=True)
    )
    resolver = MySqlPermissionResolver(org_user_repo=repo)

    allowed = resolver.has_permission(
        organization_id=uuid4(),
        user_id=uuid4(),
        action_type=ActionType.SYSTEM,
    )

    assert allowed is True


def test_resolver_returns_false_for_action_without_mapping_for_non_owner():
    repo = _OrgUserRepoStub(
        membership=_membership(role=OrganizationRole.ADMIN, is_active=True)
    )
    resolver = MySqlPermissionResolver(org_user_repo=repo)

    allowed = resolver.has_permission(
        organization_id=uuid4(),
        user_id=uuid4(),
        action_type=ActionType.SYSTEM,
    )

    assert allowed is False


def test_resolver_returns_true_when_role_is_allowed_for_action():
    repo = _OrgUserRepoStub(
        membership=_membership(role=OrganizationRole.USER, is_active=True)
    )
    resolver = MySqlPermissionResolver(org_user_repo=repo)

    allowed = resolver.has_permission(
        organization_id=uuid4(),
        user_id=uuid4(),
        action_type=ActionType.DOCUMENT_MANAGEMENT,
    )

    assert allowed is True


def test_resolver_returns_false_when_role_not_allowed():
    repo = _OrgUserRepoStub(
        membership=_membership(role=OrganizationRole.USER, is_active=True)
    )
    resolver = MySqlPermissionResolver(org_user_repo=repo)

    allowed = resolver.has_permission(
        organization_id=uuid4(),
        user_id=uuid4(),
        action_type=ActionType.CONTRACT_MANAGEMENT,
    )

    assert allowed is False

