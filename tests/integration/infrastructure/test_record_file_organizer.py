
from contract_costs.config import RECORD_DRAFT_DIR
from contract_costs.services.catalogues.record_file_organizer import RecordFileOrganizer


def test_move_to_draft(tmp_path):
    root = tmp_path
    source = tmp_path / "file.pdf"
    source.write_text("data")

    relative = RecordFileOrganizer.move_to_draft(
        root=root,
        file_path=source,
    )

    expected = root / RECORD_DRAFT_DIR / "file.pdf"

    assert not source.exists()
    assert expected.exists()
    assert relative == expected.relative_to(root)


from contract_costs.config import RECORD_RAW_DIR


def test_move_to_raw(tmp_path):
    root = tmp_path
    source = tmp_path / "a.pdf"
    source.write_text("x")

    relative = RecordFileOrganizer.move_to_raw(
        root=root,
        file_path=source,
    )

    expected = root / RECORD_RAW_DIR / "a.pdf"

    assert expected.exists()
    assert relative == expected.relative_to(root)


from contract_costs.config import RECORD_FAILED_DIR


def test_move_to_failed_creates_reason_subdir(tmp_path):
    root = tmp_path
    source = tmp_path / "bad.pdf"
    source.write_text("fail")

    relative = RecordFileOrganizer.move_to_failed(
        root=root,
        file_path=source,
        reason="Parse Error",
    )

    expected = (
        root
        / RECORD_FAILED_DIR
        / "parse_error"
        / "bad.pdf"
    )

    assert expected.exists()
    assert relative == expected.relative_to(root)


from datetime import date
from tests.builders.company_builder import CompanyBuilder


def test_move_to_owner_builds_correct_path(tmp_path):
    root = tmp_path

    owner = (
        CompanyBuilder()
        .with_name("ACME Sp. z o.o.")
        .with_tax_number("123")
        .build()
    )

    source = tmp_path / "invoice.pdf"
    source.write_text("data")

    organizer = RecordFileOrganizer()

    relative = organizer.move_to_owner(
        root=root,
        file_path=source,
        owner=owner,
        kind="cost",
        issue_date=date(2025, 3, 15),
        client_name="Mega Client",
        record_ref_number="FV/12/2025",
    )

    # owner name sanitized + upper
    expected_dir = (
        root
        / "owners"
        / "ACME_SP._Z_O.O."
        / "costs"
        / "invoices"
        / "2025"
        / "03"
    )

    expected_file = expected_dir / "MEGA__FV_12_2025.pdf"

    assert expected_file.exists()
    assert relative == expected_file.relative_to(root)


def test_move_to_owner_handles_missing_values(tmp_path):
    root = tmp_path

    owner = CompanyBuilder().build()

    source = tmp_path / "doc.pdf"
    source.write_text("x")

    organizer = RecordFileOrganizer()

    relative = organizer.move_to_owner(
        root=root,
        file_path=source,
        owner=owner,
        kind="revenue",
        issue_date=None,
        client_name="",
        record_ref_number=None,
    )

    # powinno użyć UNKNOWN i NO_NUMBER
    target = root / relative

    assert target.exists()
    assert target.name.startswith("UNKNO_")
    assert target.name.endswith(".pdf")
    assert "NO_NUMBER" in target.name
