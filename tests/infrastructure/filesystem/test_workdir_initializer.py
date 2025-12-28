import os

import pytest

from contract_costs.infrastructure.filesystem.workdir_initializer import WorkDirInitializer


@pytest.fixture(scope="session", autouse=True)
def init_test_workdir():
    os.environ["APP_ENV"] = "test"
    WorkDirInitializer.execute()

def test_work_dir_initializer_creates_all_dirs(tmp_path, monkeypatch):
    import contract_costs.config as cfg
    from contract_costs.infrastructure.filesystem.workdir_initializer import (
        WorkDirInitializer,
    )

    # 🔥 override WORK_DIR
    monkeypatch.setattr(cfg, "WORK_DIR", tmp_path)

    # i wszystkie pochodne
    monkeypatch.setattr(cfg, "OWNERS_DIR", tmp_path / "companies")
    monkeypatch.setattr(cfg, "INVOICE_INPUT_DIR", tmp_path / "invoices/incoming")
    monkeypatch.setattr(cfg, "INVOICE_FAILED_DIR", tmp_path / "invoices/failed")

    monkeypatch.setattr(cfg, "INPUTS_COMPANIES_NEW_DIR", tmp_path / "inputs/companies/new")
    monkeypatch.setattr(cfg, "INPUTS_COMPANIES_EDIT_DIR", tmp_path / "inputs/companies/edit")
    monkeypatch.setattr(cfg, "INPUTS_COMPANIES_PROCESSED_DIR", tmp_path / "inputs/companies/processed")

    monkeypatch.setattr(cfg, "INPUTS_CONTRACTS_NEW_DIR", tmp_path / "inputs/contracts/new")
    monkeypatch.setattr(cfg, "INPUTS_CONTRACTS_EDIT_DIR", tmp_path / "inputs/contracts/edit")
    monkeypatch.setattr(cfg, "INPUTS_CONTRACTS_PROCESSED_DIR", tmp_path / "inputs/contracts/processed")

    monkeypatch.setattr(cfg, "INPUTS_INVOICES_NEW_DIR", tmp_path / "inputs/invoices/new")
    monkeypatch.setattr(cfg, "INPUTS_INVOICES_ASSIGN_DIR", tmp_path / "inputs/invoices/assign")
    monkeypatch.setattr(cfg, "INPUTS_INVOICES_PROCESSED_DIR", tmp_path / "inputs/invoices/processed")

    monkeypatch.setattr(cfg, "REPORTS_DIR", tmp_path / "reports")
    monkeypatch.setattr(cfg, "LOGS_DIR", tmp_path / "logs")

    # --- execute ---
    WorkDirInitializer.execute()

    # --- assertions ---
    expected_dirs = [
        cfg.OWNERS_DIR,
        cfg.INVOICE_INPUT_DIR,
        cfg.INVOICE_FAILED_DIR,
        cfg.INPUTS_COMPANIES_NEW_DIR,
        cfg.INPUTS_COMPANIES_EDIT_DIR,
        cfg.INPUTS_COMPANIES_PROCESSED_DIR,
        cfg.INPUTS_CONTRACTS_NEW_DIR,
        cfg.INPUTS_CONTRACTS_EDIT_DIR,
        cfg.INPUTS_CONTRACTS_PROCESSED_DIR,
        cfg.INPUTS_INVOICES_NEW_DIR,
        cfg.INPUTS_INVOICES_ASSIGN_DIR,
        cfg.INPUTS_INVOICES_PROCESSED_DIR,
        cfg.REPORTS_DIR,
        cfg.LOGS_DIR,
    ]

    for d in expected_dirs:
        assert d.exists()
        assert d.is_dir()


def test_work_dir_initializer_is_idempotent(tmp_path, monkeypatch):
    import contract_costs.config as cfg
    from contract_costs.infrastructure.filesystem.workdir_initializer import (
        WorkDirInitializer,
    )

    monkeypatch.setattr(cfg, "WORK_DIR", tmp_path)
    monkeypatch.setattr(cfg, "LOGS_DIR", tmp_path / "logs")

    # pierwsze uruchomienie
    WorkDirInitializer.execute()

    # drugie uruchomienie – nie może wywalić
    WorkDirInitializer.execute()

    assert cfg.LOGS_DIR.exists()
