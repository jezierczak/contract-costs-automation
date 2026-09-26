from datetime import date
from pathlib import Path

from tests.builders.company_builder import CompanyBuilder
from contract_costs.model.company import CompanyType
from contract_costs.services.catalogues.record_file_organizer import RecordFileOrganizer


def test_record_file_organizer_sanitize_filename() -> None:
    value = RecordFileOrganizer._sanitize_filename('  a/b:c*? "x"  ')
    assert value == "A_B_C_X_"


def test_record_file_organizer_sanitize_filename_strips_trailing_dots() -> None:
    assert RecordFileOrganizer._sanitize_filename("Remontivo Sp. z o.o.") == "REMONTIVO_SP._Z_O.O"
    assert RecordFileOrganizer._sanitize_filename("...") == "UNKNOWN"


def test_record_file_organizer_build_invoice_filename() -> None:
    filename = RecordFileOrganizer._build_invoice_filename(
        client_name="Very Long Client Name",
        invoice_number="FV/1/2026",
        original=Path("x.pdf"),
    )
    assert filename.endswith(".pdf")
    assert filename.startswith("VERY_")


def test_record_file_organizer_move_to_owner_cost(tmp_path: Path) -> None:
    root = tmp_path / "org"
    root.mkdir()
    source = root / "invoice.pdf"
    source.write_text("x", encoding="utf-8")

    owner = (
        CompanyBuilder()
        .with_name("Own Company")
        .with_role(CompanyType.OWN)
        .build()
    )
    organizer = RecordFileOrganizer()

    rel = organizer.move_to_owner(
        root=root,
        file_path=source,
        owner=owner,
        kind="cost",
        issue_date=date(2026, 2, 17),
        client_name="Client X",
        record_ref_number="FV/1/2026",
    )

    assert "owners" in rel.as_posix()
    assert "costs" in rel.as_posix()
    assert (root / rel).exists()


def test_record_file_organizer_move_to_failed_sanitizes_reason(tmp_path: Path) -> None:
    root = tmp_path / "org"
    root.mkdir()
    source = root / "invoice.pdf"
    source.write_text("x", encoding="utf-8")

    rel = RecordFileOrganizer.move_to_failed(
        root=root,
        file_path=source,
        reason="Bad/Reason",
    )
    assert "bad_reason" in rel.as_posix()
    assert (root / rel).exists()
