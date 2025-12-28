from contract_costs.cli.main import main


def test_cli_routes_add_company(monkeypatch):
    called = {}

    def fake_handle():
        called["ok"] = True

    monkeypatch.setattr(
        "contract_costs.cli.main.handle_add_company",
        fake_handle,
    )

    main(["add", "company"])

    assert called["ok"] is True
