from dataclasses import dataclass
from uuid import uuid4

import pytest

from contract_costs.action_bus.action import Action
from contract_costs.action_bus.action_bus import ActionBus
from contract_costs.action_bus.action_type import ActionType, action_type


class _PermissionValidatorStub:
    def __init__(self) -> None:
        self.calls = []

    def validate(self, action) -> None:
        self.calls.append(action)


class _PermissionValidatorDeny:
    def validate(self, action) -> None:
        raise PermissionError("Not allowed")


class _DummyUow:
    def __init__(self) -> None:
        self.entered = False
        self.exited = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self.exited = True
        return False


@dataclass(frozen=True, slots=True)
@action_type(ActionType.VIEW)
class _OkAction(Action):
    organization_id: object
    actor_user_id: object


@dataclass(frozen=True, slots=True)
class _MissingDecoratorAction(Action):
    organization_id: object
    actor_user_id: object


class _Handler:
    def __init__(self, result="ok") -> None:
        self.result = result
        self.calls = []

    def execute(self, *, action, uow):
        self.calls.append((action, uow))
        return self.result


class _ErrorHandler:
    def execute(self, *, action, uow):
        raise RuntimeError("boom")


def test_action_bus_runs_handler_inside_uow_context():
    validator = _PermissionValidatorStub()
    uow = _DummyUow()
    bus = ActionBus(permission_validator=validator, uow_factory=lambda: uow)
    handler = _Handler(result=123)
    action = _OkAction(organization_id=uuid4(), actor_user_id=uuid4())

    result = bus.execute(action=action, handler=handler)

    assert result == 123
    assert validator.calls == [action]
    assert len(handler.calls) == 1
    assert handler.calls[0][0] == action
    assert handler.calls[0][1] is uow
    assert uow.entered is True
    assert uow.exited is True


def test_action_bus_raises_when_action_is_missing_decorator():
    bus = ActionBus(
        permission_validator=_PermissionValidatorStub(),
        uow_factory=lambda: _DummyUow(),
    )
    action = _MissingDecoratorAction(organization_id=uuid4(), actor_user_id=uuid4())

    with pytest.raises(RuntimeError, match="missing @action_type"):
        bus.execute(action=action, handler=_Handler())


def test_action_bus_raises_for_missing_handler():
    bus = ActionBus(
        permission_validator=_PermissionValidatorStub(),
        uow_factory=lambda: _DummyUow(),
    )
    action = _OkAction(organization_id=uuid4(), actor_user_id=uuid4())

    with pytest.raises(ValueError, match="No handler registered"):
        bus.execute(action=action, handler=None)


def test_action_bus_raises_for_handler_without_execute():
    bus = ActionBus(
        permission_validator=_PermissionValidatorStub(),
        uow_factory=lambda: _DummyUow(),
    )
    action = _OkAction(organization_id=uuid4(), actor_user_id=uuid4())

    with pytest.raises(TypeError, match="execute"):
        bus.execute(action=action, handler=object())


def test_action_bus_propagates_handler_exceptions():
    bus = ActionBus(
        permission_validator=_PermissionValidatorStub(),
        uow_factory=lambda: _DummyUow(),
    )
    action = _OkAction(organization_id=uuid4(), actor_user_id=uuid4())

    with pytest.raises(RuntimeError, match="boom"):
        bus.execute(action=action, handler=_ErrorHandler())


def test_action_bus_stops_before_handler_when_permission_denied():
    uow = _DummyUow()
    bus = ActionBus(
        permission_validator=_PermissionValidatorDeny(),
        uow_factory=lambda: uow,
    )
    handler = _Handler()
    action = _OkAction(organization_id=uuid4(), actor_user_id=uuid4())

    with pytest.raises(PermissionError, match="Not allowed"):
        bus.execute(action=action, handler=handler)

    assert handler.calls == []
    assert uow.entered is False
    assert uow.exited is False


def test_action_requires_org_and_actor_ids_on_construction():
    with pytest.raises(TypeError):
        _OkAction()  # type: ignore[call-arg]
