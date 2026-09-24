import pytest

import contract_costs.config as cfg
from contract_costs.cli import main as cli_main


def test_prod_requires_typing_prod(monkeypatch):
    # nawet gdy zmienna środowiskowa mówi "test" (np. nadpisana przez plik .env)
    monkeypatch.setattr(cfg, "APP_ENV", "prod")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setattr("builtins.input", lambda _prompt: "nie")
    monkeypatch.setattr(
        cli_main,
        "build_cli_parser",
        lambda: pytest.fail("CLI must not run without PROD confirmation"),
    )

    with pytest.raises(SystemExit):
        cli_main.main([])
