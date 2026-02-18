from pathlib import Path
from uuid import uuid4

import pytest

from contract_costs.services.documents.prepare.dto.prepare_documents_command import PrepareDocumentsCommand
from contract_costs.services.documents.prepare.prepare_documents_service import PrepareDocumentsService
from contract_costs.services.documents.process.dto.process_document_command import ProcessDocumentCommand
from contract_costs.services.documents.process.process_document_service import ProcessDocumentService
from contract_costs.services.documents.upload.dto.upload_document_command import UploadDocumentCommand
from contract_costs.services.documents.upload.upload_document_service import UploadDocumentService
from contract_costs.unit_of_work.inmemory_unit_of_work import InMemoryUnitOfWork


class _FakeCompanyEvaluate:
    def evaluate_from_tax(self, **kwargs):
        raise RuntimeError("no companies")


class _FakeParser:
    def execute(self, **kwargs):
        raise AssertionError("should not be called in this test")


def test_upload_document_raises_for_missing_file():
    service = UploadDocumentService()
    uow = InMemoryUnitOfWork()

    with pytest.raises(FileNotFoundError):
        service.execute(
            action=UploadDocumentCommand(
                organization_id=uuid4(),
                actor_user_id=uuid4(),
                file_path=Path("missing-file.pdf"),
            ),
            uow=uow,
        )


def test_process_document_raises_when_document_missing():
    service = ProcessDocumentService(parse_service=_FakeParser())

    with pytest.raises(ValueError, match="Document not found"):
        service.execute(
            action=ProcessDocumentCommand(
                organization_id=uuid4(),
                actor_user_id=uuid4(),
                document_id=uuid4(),
                force=False,
            ),
            uow=InMemoryUnitOfWork(),
        )


def test_prepare_documents_returns_empty_bundle_when_no_docs():
    service = PrepareDocumentsService(company_evaluate=_FakeCompanyEvaluate())

    result = service.execute(
        action=PrepareDocumentsCommand(
            organization_id=uuid4(),
            actor_user_id=uuid4(),
        ),
        uow=InMemoryUnitOfWork(),
    )

    assert result.documents == []
