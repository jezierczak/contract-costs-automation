from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from contract_costs.cli.commands import init_company_contracts as mod


def _services(org_id, user_id, result=None):
    return SimpleNamespace(
        context=SimpleNamespace(
            current_organization_id=lambda: org_id,
            current_user_id=lambda: user_id,
        ),
        action_bus=SimpleNamespace(execute=Mock(return_value=result)),
        backfill_import_payments=object(),
        backfill_system_contracts=object(),
    )


@pytest.mark.parametrize("apply", [False, True])
def test_backfill_import_payments_passes_context_and_apply_flag(monkeypatch, capsys, apply):
    org_id, user_id = uuid4(), uuid4()
    services = _services(org_id, user_id, result=[])
    monkeypatch.setattr(mod, "get_services", lambda: services)

    mod.handle_backfill_import_payments(SimpleNamespace(apply=apply))

    call = services.action_bus.execute.call_args.kwargs
    assert call["action"].organization_id == org_id
    assert call["action"].actor_user_id == user_id
    assert call["action"].apply is apply
    assert call["handler"] is services.backfill_import_payments
    assert "Rekordów: 0" in capsys.readouterr().out


def test_system_backfill_passes_context(monkeypatch):
    org_id, user_id = uuid4(), uuid4()
    services = _services(org_id, user_id)
    monkeypatch.setattr(mod, "get_services", lambda: services)

    mod.handle_system_backfill(SimpleNamespace())

    call = services.action_bus.execute.call_args.kwargs
    assert call["action"].actor_user_id == user_id
