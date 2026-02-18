from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

from tests.builders.company_builder import CompanyBuilder
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentSource
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.services.catalogues.record_file_workworkflow_service import (
    RecordFileWorkflowService,
)


def _make_uow(*, buyer=None, seller=None):
    return SimpleNamespace(
        companies=SimpleNamespace(
            get=Mock(side_effect=[buyer, seller]),
        ),
        documents=SimpleNamespace(update=Mock()),
    )


def test_record_file_workflow_service_returns_when_no_documents(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("contract_costs.config.WORK_DIR", tmp_path)
    service = RecordFileWorkflowService(file_organizer=Mock())
    uow = _make_uow()
    record = FinancialRecordBuilder().with_documents([]).build()

    service.sync(
        organization_id=record.organization_id,
        record=record,
        uow=uow,
    )

    assert uow.documents.update.call_count == 0


def test_record_file_workflow_service_moves_deleted_to_trash(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("contract_costs.config.WORK_DIR", tmp_path)
    org_id = uuid4()
    org_root = tmp_path / str(org_id)
    org_root.mkdir(parents=True)
    rel = "incoming/documents/a.pdf"
    f = org_root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("x", encoding="utf-8")

    doc = DocumentBuilder().with_file_path(rel).with_document_source(DocumentSource.PDF).build()
    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.DELETED)
        .with_documents([doc])
        .build()
    )

    organizer = Mock()
    organizer.move_to_trash.return_value = Path("trash/a.pdf")
    service = RecordFileWorkflowService(file_organizer=organizer)
    uow = _make_uow()

    service.sync(organization_id=org_id, record=record, uow=uow)

    assert organizer.move_to_trash.call_count == 1
    assert uow.documents.update.call_count == 1
    assert record.documents[0].file_path == "trash/a.pdf"


def test_record_file_workflow_service_moves_cost_to_owner_when_buyer_is_own(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("contract_costs.config.WORK_DIR", tmp_path)
    org_id = uuid4()
    org_root = tmp_path / str(org_id)
    org_root.mkdir(parents=True)
    rel = "incoming/documents/b.pdf"
    f = org_root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("x", encoding="utf-8")

    buyer = CompanyBuilder().with_role(CompanyType.OWN).with_name("Own").build()
    seller = CompanyBuilder().with_role(CompanyType.SUPPLIER).with_name("Supp").build()
    doc = DocumentBuilder().with_file_path(rel).build()
    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_buyer_id(buyer.id)
        .with_seller_id(seller.id)
        .with_documents([doc])
        .build()
    )

    organizer = Mock()
    organizer.move_to_owner.return_value = Path("owners/own/costs/invoices/2026/02/X.pdf")
    service = RecordFileWorkflowService(file_organizer=organizer)
    uow = _make_uow(buyer=buyer, seller=seller)

    service.sync(organization_id=org_id, record=record, uow=uow)

    assert organizer.move_to_owner.call_count == 1
    kwargs = organizer.move_to_owner.call_args.kwargs
    assert kwargs["kind"] == "cost"
    assert uow.documents.update.call_count == 1


def test_record_file_workflow_service_moves_to_draft_when_missing_company(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("contract_costs.config.WORK_DIR", tmp_path)
    org_id = uuid4()
    org_root = tmp_path / str(org_id)
    org_root.mkdir(parents=True)
    rel = "incoming/documents/c.pdf"
    f = org_root / rel
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("x", encoding="utf-8")

    doc = DocumentBuilder().with_file_path(rel).build()
    record = FinancialRecordBuilder().with_organization_id(org_id).with_documents([doc]).build()

    organizer = Mock()
    organizer.move_to_draft.return_value = Path("draft/c.pdf")
    service = RecordFileWorkflowService(file_organizer=organizer)
    uow = _make_uow(buyer=None, seller=None)

    service.sync(organization_id=org_id, record=record, uow=uow)

    assert organizer.move_to_draft.call_count == 1
    assert uow.documents.update.call_count == 1

