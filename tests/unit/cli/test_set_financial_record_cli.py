from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from contract_costs.cli.commands.set import set_financial_record_action as mod
from contract_costs.services.financial_records.actions.dto.invoice_action_command import (
    FinancialRecordAction,
    FinancialRecordActionCommand,
)


def _services(org_id, user_id):
    return SimpleNamespace(
        context=SimpleNamespace(
            current_organization_id=lambda: org_id,
            current_user_id=lambda: user_id,
        ),
        action_bus=SimpleNamespace(execute=Mock()),
        financial_record_action_service=object(),
    )


def test_handle_set_financial_record_uses_uuid_selector(monkeypatch) -> None:
    org_id = uuid4()
    user_id = uuid4()
    rec_id = uuid4()
    services = _services(org_id, user_id)
    monkeypatch.setattr(mod, "get_services", lambda: services)

    mod.handle_set_financial_record(SimpleNamespace(action="paid", ref=str(rec_id)))

    call = services.action_bus.execute.call_args.kwargs
    assert isinstance(call["action"], FinancialRecordActionCommand)
    assert call["action"].action == FinancialRecordAction.MARK_PAID
    assert call["action"].selectors[0].record_id == rec_id
    assert call["handler"] is services.financial_record_action_service


def test_handle_set_financial_record_uses_reference_selector_for_non_uuid(monkeypatch) -> None:
    org_id = uuid4()
    user_id = uuid4()
    services = _services(org_id, user_id)
    monkeypatch.setattr(mod, "get_services", lambda: services)

    mod.handle_set_financial_record(SimpleNamespace(action="reopen", ref="FV/2026/01"))
    call = services.action_bus.execute.call_args.kwargs
    assert call["action"].action == FinancialRecordAction.REOPEN
    assert call["action"].selectors[0].record_reference == "FV/2026/01"


def test_handle_set_financial_record_invalid_action_does_not_dispatch(monkeypatch, capsys) -> None:
    org_id = uuid4()
    user_id = uuid4()
    services = _services(org_id, user_id)
    monkeypatch.setattr(mod, "get_services", lambda: services)

    mod.handle_set_financial_record(SimpleNamespace(action="bad", ref="FV/1"))
    out = capsys.readouterr().out

    assert "Allowed:" in out
    assert services.action_bus.execute.call_count == 0

