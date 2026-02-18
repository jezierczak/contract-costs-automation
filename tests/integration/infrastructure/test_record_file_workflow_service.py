from contract_costs.common.ids import new_uuid
from contract_costs.model.financial_record import FinancialRecordStatus
from tests.builders.company_builder import CompanyBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.document_builder import DocumentBuilder
from contract_costs.model.company import CompanyType



def test_deleted_record_moves_to_trash(tmp_path, workflow_service, uow):
    service = workflow_service
    document_repo = uow.documents

    import contract_costs.config as cfg
    cfg.WORK_DIR = tmp_path

    org_id = new_uuid()

    root = tmp_path / str(org_id)
    root.mkdir()

    source = root / "doc.pdf"
    source.write_text("x")

    document = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_file_path("doc.pdf")
        .build()
    )

    document_repo.add(document)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.DELETED)
        .with_documents([document])
        .build()
    )

    service.sync(
        organization_id=org_id,
        record=record,
        uow=uow,
    )

    assert not source.exists()


def test_cost_record_moves_to_owner_directory(tmp_path, workflow_service, uow):
    service = workflow_service
    company_repo = uow.companies
    document_repo = uow.documents

    import contract_costs.config as cfg
    cfg.WORK_DIR = tmp_path

    org_id = new_uuid()
    root = tmp_path / str(org_id)
    root.mkdir()

    # OWN company = buyer
    owner = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_name("My Company")
        .build()
    )

    seller = (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.SUPPLIER)
        .with_name("Supplier X")
        .build()
    )

    company_repo.add(owner)
    company_repo.add(seller)

    source = root / "doc.pdf"
    source.write_text("x")

    document = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_file_path("doc.pdf")
        .build()
    )

    document_repo.add(document)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_buyer_id(owner.id)
        .with_seller_id(seller.id)
        .with_documents([document])
        .build()
    )

    service.sync(
        organization_id=org_id,
        record=record,
        uow=uow,
    )

    # plik powinien być przeniesiony
    assert not source.exists()

    # dokument w repo powinien mieć zmienioną ścieżkę
    updated_doc = document_repo.get(
        organization_id=org_id,
        document_id=document.id,
    )

    assert "costs" in updated_doc.file_path


def test_missing_parties_goes_to_draft(tmp_path, workflow_service, uow):
    service = workflow_service
    document_repo = uow.documents

    import contract_costs.config as cfg
    cfg.WORK_DIR = tmp_path

    org_id = new_uuid()
    root = tmp_path / str(org_id)
    root.mkdir()

    source = root / "doc.pdf"
    source.write_text("x")

    document = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_file_path("doc.pdf")
        .build()
    )

    document_repo.add(document)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_buyer_id(None)
        .with_seller_id(None)
        .with_documents([document])
        .build()
    )

    service.sync(
        organization_id=org_id,
        record=record,
        uow=uow,
    )

    updated = document_repo.get(
        organization_id=org_id,
        document_id=document.id,
    )

    assert "draft" in updated.file_path
