from contract_costs.cli.main import main


def test_cli_routes_add_company(monkeypatch):
    called = {}

    def fake_handle():
        called["ok"] = True

    monkeypatch.setattr(
         "contract_costs.cli.commands.add.add_company._run_add_company_interactive",
        fake_handle,
    )

    main(["add", "company"])

    assert called["ok"] is True
