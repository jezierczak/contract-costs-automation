import hashlib
from pathlib import Path

import pytest

from contract_costs.model.document import DocumentSource
from contract_costs.services.documents.upload.upload_document_service import UploadDocumentService


def test_resolve_source_by_extension():
    assert UploadDocumentService._resolve_source(Path("a.pdf")) == DocumentSource.PDF
    assert UploadDocumentService._resolve_source(Path("a.xml")) == DocumentSource.KSEF
    assert UploadDocumentService._resolve_source(Path("a.jpg")) == DocumentSource.IMAGE


def test_resolve_source_raises_for_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file extension"):
        UploadDocumentService._resolve_source(Path("a.txt"))


def test_calculate_hash_matches_sha256(tmp_path):
    file_path = tmp_path / "payload.pdf"
    content = b"hello-doc"
    file_path.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    actual = UploadDocumentService._calculate_hash(file_path)

    assert actual == expected
