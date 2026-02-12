from pathlib import Path

from contract_costs.config import DOCUMENTS_PROCESSING_DIR
from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer


def test_move_to_processing(tmp_path):
    root = tmp_path
    source_file = tmp_path / "invoice.pdf"
    source_file.write_text("test")

    relative_path = DocumentFileOrganizer.move_to_processing(
        root=root,
        file_path=source_file,
    )

    expected_path = root / DOCUMENTS_PROCESSING_DIR / "invoice.pdf"

    assert not source_file.exists()
    assert expected_path.exists()
    assert relative_path == expected_path.relative_to(root)

from contract_costs.config import DOCUMENTS_RAW_DIR


def test_move_to_raw(tmp_path):
    root = tmp_path
    source_file = tmp_path / "doc.pdf"
    source_file.write_text("x")

    relative_path = DocumentFileOrganizer.move_to_raw(
        root=root,
        file_path=source_file,
    )

    expected_path = root / DOCUMENTS_RAW_DIR / "doc.pdf"

    assert expected_path.exists()
    assert relative_path == expected_path.relative_to(root)


from contract_costs.config import DOCUMENTS_FAILED_DIR


def test_move_to_failed_creates_reason_subdir(tmp_path):
    root = tmp_path
    source_file = tmp_path / "broken.pdf"
    source_file.write_text("fail")

    relative_path = DocumentFileOrganizer.move_to_failed(
        root=root,
        file_path=source_file,
        reason="ParseError",
    )

    expected_path = (
        root
        / DOCUMENTS_FAILED_DIR
        / "parseerror"
        / "broken.pdf"
    )

    assert expected_path.exists()
    assert relative_path == expected_path.relative_to(root)


def test_move_overwrites_existing_file(tmp_path):
    root = tmp_path

    target_dir = root / DOCUMENTS_PROCESSING_DIR
    target_dir.mkdir(parents=True)

    existing = target_dir / "file.pdf"
    existing.write_text("old")

    source = tmp_path / "file.pdf"
    source.write_text("new")

    DocumentFileOrganizer.move_to_processing(
        root=root,
        file_path=source,
    )

    assert existing.read_text() == "new"
