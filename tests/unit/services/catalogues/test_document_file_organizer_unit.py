from pathlib import Path

import pytest

from contract_costs.services.catalogues.document_file_organizer import DocumentFileOrganizer


def test_document_file_organizer_moves_file_to_processing(tmp_path: Path) -> None:
    root = tmp_path / "org"
    root.mkdir()
    source = root / "doc.pdf"
    source.write_text("x", encoding="utf-8")

    rel = DocumentFileOrganizer.move_to_processing(root=root, file_path=source)

    assert (root / rel).exists()
    assert not source.exists()


def test_document_file_organizer_moves_file_to_all_document_buckets(tmp_path: Path) -> None:
    root = tmp_path / "org"
    root.mkdir()

    for move_fn, kwargs in [
        (DocumentFileOrganizer.move_to_raw, {}),
        (DocumentFileOrganizer.move_to_trash, {}),
        (DocumentFileOrganizer.move_to_skipped, {}),
        (DocumentFileOrganizer.move_to_duplicates, {}),
        (DocumentFileOrganizer.move_to_failed, {"reason": "OCR"}),
    ]:
        source = root / f"{move_fn.__name__}.pdf"
        source.write_text("x", encoding="utf-8")
        rel = move_fn(root=root, file_path=source, **kwargs)
        assert (root / rel).exists()
        assert not source.exists()


def test_document_file_organizer_delete_file_is_idempotent(tmp_path: Path) -> None:
    root = tmp_path / "org"
    root.mkdir()
    rel = "documents/raw/a.pdf"
    target = root / rel
    target.parent.mkdir(parents=True)
    target.write_text("x", encoding="utf-8")

    DocumentFileOrganizer.delete_file(root=root, relative_path=rel)
    DocumentFileOrganizer.delete_file(root=root, relative_path=rel)
    assert not target.exists()


def test_document_file_organizer_delete_file_blocks_path_traversal(tmp_path: Path) -> None:
    root = tmp_path / "org"
    root.mkdir()

    with pytest.raises(RuntimeError, match="outside organization root"):
        DocumentFileOrganizer.delete_file(root=root, relative_path="../evil.txt")
    with pytest.raises(RuntimeError, match="outside organization root"):
        DocumentFileOrganizer.delete_file(root=root, relative_path="..\\evil.txt")


def test_document_file_organizer_delete_file_rejects_directory(tmp_path: Path) -> None:
    root = tmp_path / "org"
    root.mkdir()
    d = root / "documents"
    d.mkdir()

    with pytest.raises(RuntimeError, match="Refusing to delete directory"):
        DocumentFileOrganizer.delete_file(root=root, relative_path="documents")
