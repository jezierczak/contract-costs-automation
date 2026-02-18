from types import SimpleNamespace
from uuid import uuid4

from contract_costs.model.company import CompanyType
from contract_costs.cli.commands.add import add_company as mod


def _company_data() -> dict:
    return {
        "name": "Supplier X",
        "tax_number": "1234567890",
        "role": CompanyType.SUPPLIER,
        "description": None,
        "address_street": None,
        "address_city": None,
        "address_zip_code": None,
        "address_country": None,
        "phone_number": None,
        "email": None,
        "bank_account_number": None,
        "bank_account_country_code": None,
    }


def test_handle_add_company_non_interactive_returns_early(monkeypatch) -> None:
    called = {"n": 0}
    monkeypatch.setattr(mod, "_run_add_company_interactive", lambda: called.__setitem__("n", called["n"] + 1))
    mod.handle_add_company(SimpleNamespace(non_interactive=True))
    assert called["n"] == 0


def test_run_add_company_interactive_dispatches_to_adapter(monkeypatch) -> None:
    org_id = uuid4()
    user_id = uuid4()
    data = _company_data()

    monkeypatch.setattr(mod, "interactive_prompt", lambda _fields: data)
    monkeypatch.setattr("builtins.input", lambda _msg="": "y")

    services = SimpleNamespace(
        context=SimpleNamespace(
            current_organization_id=lambda: org_id,
            current_user_id=lambda: user_id,
        ),
        action_bus=object(),
        create_company=object(),
    )
    monkeypatch.setattr(mod, "get_services", lambda: services)

    captured = {}

    def _fake_create_company_from_cli(**kwargs):
        captured.update(kwargs)

    monkeypatch.setattr(mod, "create_company_from_cli", _fake_create_company_from_cli)

    mod._run_add_company_interactive()

    assert captured["data"] == data
    assert captured["organization_id"] == org_id
    assert captured["actor_user_id"] == user_id
    assert captured["action_bus"] is services.action_bus
    assert captured["create_company_service"] is services.create_company


def test_run_add_company_interactive_cancelled(monkeypatch) -> None:
    monkeypatch.setattr(mod, "interactive_prompt", lambda _fields: _company_data())
    monkeypatch.setattr("builtins.input", lambda _msg="": "n")

    called = {"n": 0}
    monkeypatch.setattr(mod, "create_company_from_cli", lambda **_kwargs: called.__setitem__("n", called["n"] + 1))

    mod._run_add_company_interactive()
    assert called["n"] == 0

