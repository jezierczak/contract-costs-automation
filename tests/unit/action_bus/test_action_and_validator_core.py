from dataclasses import dataclass
from uuid import uuid4

import pytest

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_type import ActionType, action_type
from contract_costs.action_bus.permission_resolver import PermissionResolver
from contract_costs.action_bus.permission_validator import PermissionValidator


class _ResolverStub(PermissionResolver):
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed
        self.calls = []

    def has_permission(self, *, organization_id, user_id, action_type) -> bool:
        self.calls.append((organization_id, user_id, action_type))
        return self.allowed


@dataclass(frozen=True, slots=True)
@action_type(ActionType.DOCUMENT_MANAGEMENT)
class _DecoratedAction(Action):
    organization_id: object
    actor_user_id: object


@dataclass(frozen=True, slots=True)
class _UndecoratedAction(Action):
    organization_id: object
    actor_user_id: object


@dataclass(frozen=True, slots=True)
@action_type(ActionType.SYSTEM)
class _SystemAction(Action):
    organization_id: object
    actor_user_id: object


@dataclass(frozen=True, slots=True)
@action_type(ActionType.VIEW)
class _NoOrgAction(Action):
    pass


def test_action_property_returns_decorated_action_type():
    action = _DecoratedAction(organization_id=uuid4(), actor_user_id=uuid4())
    assert action.action_type is ActionType.DOCUMENT_MANAGEMENT


def test_action_property_raises_without_decorator():
    action = _UndecoratedAction(organization_id=uuid4(), actor_user_id=uuid4())
    with pytest.raises(RuntimeError, match="missing @action_type"):
        _ = action.action_type


def test_permission_validator_bypasses_system_action():
    resolver = _ResolverStub(allowed=False)
    validator = PermissionValidator(permission_resolver=resolver)

    validator.validate(_SystemAction(organization_id=uuid4(), actor_user_id=uuid4()))

    assert resolver.calls == []


def test_permission_validator_calls_resolver_for_org_action():
    org_id = uuid4()
    user_id = uuid4()
    resolver = _ResolverStub(allowed=True)
    validator = PermissionValidator(permission_resolver=resolver)

    validator.validate(_DecoratedAction(organization_id=org_id, actor_user_id=user_id))

    assert len(resolver.calls) == 1
    call = resolver.calls[0]
    assert call[0] == org_id
    assert call[1] == user_id
    assert call[2] is ActionType.DOCUMENT_MANAGEMENT


def test_permission_validator_raises_when_not_allowed():
    resolver = _ResolverStub(allowed=False)
    validator = PermissionValidator(permission_resolver=resolver)

    with pytest.raises(PermissionError, match="Not allowed"):
        validator.validate(_DecoratedAction(organization_id=uuid4(), actor_user_id=uuid4()))


def test_permission_validator_ignores_action_without_org_fields():
    resolver = _ResolverStub(allowed=False)
    validator = PermissionValidator(permission_resolver=resolver)

    validator.validate(_NoOrgAction())

    assert resolver.calls == []


def test_permission_validator_raises_when_action_type_is_none():
    resolver = _ResolverStub(allowed=True)
    validator = PermissionValidator(permission_resolver=resolver)

    class _BrokenAction:
        action_type = None

    with pytest.raises(RuntimeError, match="Missing action_type"):
        validator.validate(_BrokenAction())
