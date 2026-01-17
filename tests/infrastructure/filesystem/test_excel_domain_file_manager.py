import pytest
from pathlib import Path

from contract_costs.infrastructure.filesystem.excel_domain_file_manager import (
    ExcelDomainFileManager,
)


def create_file(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("test")


def test_prepare_creates_new_when_no_active(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "invoices")

    target = fm.prepare_target()

    assert target.name == "invoices.xlsx"
    assert target.parent == tmp_path
    assert not target.exists()

    assert (tmp_path / "replaced").exists()
    assert (tmp_path / "processed").exists()



def test_prepare_moves_existing_to_replaced(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "invoices")

    active = tmp_path / "invoices.xlsx"
    create_file(active)

    target = fm.prepare_target()

    replaced_dir = tmp_path / "replaced"
    replaced_files = list(replaced_dir.iterdir())

    assert len(replaced_files) == 1
    assert replaced_files[0].name.startswith("invoices_")

    # ❗ POPRAWKA
    assert target == tmp_path / "invoices.xlsx"
    assert not target.exists()



def test_prepare_multiple_replacements(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "contracts")

    for _ in range(2):
        target = fm.prepare_target()
        target.write_text("dummy")  # symulacja exportera

    replaced_files = list((tmp_path / "replaced").iterdir())
    assert len(replaced_files) == 1



def test_get_active_file(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "companies")

    active = tmp_path / "companies.xlsx"
    create_file(active)

    found = fm.get_active_file()
    assert found == active

def test_get_active_file_missing(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "companies")

    with pytest.raises(FileNotFoundError):
        fm.get_active_file()


def test_get_active_file_ignores_other_files(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "companies")

    active = tmp_path / "companies.xlsx"
    other = tmp_path / "companies_COPY.xlsx"

    create_file(active)
    create_file(other)

    found = fm.get_active_file()
    assert found == active



def test_mark_processed(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "invoices")

    active = tmp_path / "invoices.xlsx"
    create_file(active)

    fm.mark_processed()

    processed = list((tmp_path / "processed").iterdir())
    assert len(processed) == 1
    assert processed[0].name.startswith("invoices_")
    assert not active.exists()


def test_mark_processed_without_active(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "invoices")

    with pytest.raises(FileNotFoundError):
        fm.mark_processed()


def test_full_lifecycle(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "contracts")

    # prepare
    target = fm.prepare_target()
    create_file(target)

    # apply
    active = fm.get_active_file()
    assert active == target

    fm.mark_processed()

    processed_files = list((tmp_path / "processed").iterdir())
    assert len(processed_files) == 1
    assert not target.exists()


def test_prepare_after_processed(tmp_path):
    fm = ExcelDomainFileManager(tmp_path, "contracts")

    create_file(tmp_path / "contracts.xlsx")
    fm.mark_processed()

    new_target = fm.prepare_target()

    assert new_target == tmp_path / "contracts.xlsx"
    assert not new_target.exists()

    # opcjonalnie: symulacja exportera
    new_target.write_text("dummy")
    assert new_target.exists()

