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


def test_upload_stores_ksef_number(tmp_path, monkeypatch):
    from uuid import uuid4

    import contract_costs.config as cfg
    from contract_costs.services.documents.upload.dto.upload_document_command import UploadDocumentCommand
    from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork

    monkeypatch.setattr(cfg, "WORK_DIR", tmp_path / "work")
    organization_id = uuid4()
    incoming = tmp_path / "work" / str(organization_id) / "incoming"
    incoming.mkdir(parents=True)
    source = incoming / "ksef_1111111111_x.xml"
    source.write_text("<Faktura/>", encoding="utf-8")
    uow = InMemoryUnitOfWork()

    document_id = UploadDocumentService().execute(
        action=UploadDocumentCommand(
            organization_id=organization_id,
            actor_user_id=uuid4(),
            file_path=source,
            ksef_number="1111111111-20260915-0100001AF629-AF",
        ),
        uow=uow,
    )

    document = uow.documents.get(organization_id=organization_id, document_id=document_id)
    assert document.ksef_number == "1111111111-20260915-0100001AF629-AF"
