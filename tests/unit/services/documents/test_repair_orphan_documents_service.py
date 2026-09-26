from uuid import uuid4

from contract_costs.model.document import DocumentStatus
from contract_costs.services.documents.migration.repair_orphan_documents_command import (
    RepairOrphanDocumentsCommand,
)
from contract_costs.services.documents.migration.repair_orphan_documents_service import (
    RepairOrphanDocumentsService,
)
from tests.builders.document_builder import DocumentBuilder

ORG = uuid4()


def _document(uow, tmp_path, *, status, record_id=None, with_file=True):
    relative = f"owners/X/costs/invoices/2026/07/{uuid4().hex}.pdf"
    if with_file:
        path = tmp_path / str(ORG) / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"%PDF")
    document = (
        DocumentBuilder()
        .with_organization_id(ORG)
        .with_document_status(status)
        .with_financial_record_id(record_id)
        .with_file_path(relative)
        .build()
    )
    uow.documents.add(document)
    return document


def _run(uow, tmp_path, apply=False):
    return RepairOrphanDocumentsService(work_dir=tmp_path).execute(
        action=RepairOrphanDocumentsCommand(organization_id=ORG, actor_user_id=uuid4(), apply=apply),
        uow=uow,
    )


def test_lists_only_applied_documents_without_record(uow, tmp_path):
    orphan = _document(uow, tmp_path, status=DocumentStatus.APPLIED)
    _document(uow, tmp_path, status=DocumentStatus.APPLIED, record_id=uuid4())
    _document(uow, tmp_path, status=DocumentStatus.READY)

    fixes = _run(uow, tmp_path)

    assert [f.document_id for f in fixes] == [orphan.id]
    assert uow.documents.get(organization_id=ORG, document_id=orphan.id).document_status == DocumentStatus.APPLIED


def test_apply_moves_file_back_and_sets_ready(uow, tmp_path):
    orphan = _document(uow, tmp_path, status=DocumentStatus.APPLIED)

    [fix] = _run(uow, tmp_path, apply=True)

    stored = uow.documents.get(organization_id=ORG, document_id=orphan.id)
    assert stored.document_status == DocumentStatus.READY
    assert stored.file_path == fix.new_path != orphan.file_path
    assert (tmp_path / str(ORG) / stored.file_path).exists()


def test_missing_file_only_changes_status(uow, tmp_path):
    orphan = _document(uow, tmp_path, status=DocumentStatus.APPLIED, with_file=False)

    [fix] = _run(uow, tmp_path, apply=True)

    stored = uow.documents.get(organization_id=ORG, document_id=orphan.id)
    assert fix.file_missing
    assert stored.document_status == DocumentStatus.READY
    assert stored.file_path == orphan.file_path
