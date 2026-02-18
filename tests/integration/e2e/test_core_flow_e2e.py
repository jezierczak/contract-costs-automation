from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from contract_costs.common.time import utc_now
from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.document import DocumentSource
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.model.contract_node_progress import ContractNodeProgress
from contract_costs.model.value_direction import ValueDirection
from contract_costs.services.documents.query.list_docuemnts_query_command import (
    ListDocumentsQueryCommand,
)
from contract_costs.services.reports.dto.generate_contract_cost_report_query import (
    GenerateContractCostReportQuery,
)
from contract_costs.services.snapshots.dto.create_contract_snapshot_command import (
    CreateContractSnapshotCommand,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from tests.builders.value_type_builder import ValueTypeBuilder
from tests.helpers.contracts_helpers import make_contract_node


def test_core_flow_e2e_uses_shared_services_memory_context(services_memory):
    uow = services_memory.uow

    organization_id = uuid4()
    actor_user_id = uuid4()
    snapshot_date = date.today()

    owner = (
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.OWN)
        .with_tax_number("1111111111")
        .with_name("Own Company")
        .build()
    )
    supplier = (
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.SUPPLIER)
        .with_tax_number("2222222222")
        .with_name("Supplier Company")
        .build()
    )
    uow.companies.add(owner)
    uow.companies.add(supplier)

    contract = (
        ContractBuilder()
        .with_organization_id(organization_id)
        .with_owner(owner)
        .with_client(supplier)
        .with_code("C-E2E-1")
        .build()
    )
    uow.contracts.add(contract)

    root = make_contract_node(
        organization_id=organization_id,
        contract_id=contract.id,
        code="ROOT",
        budget=None,
        parent_id=None,
    )
    leaf = make_contract_node(
        organization_id=organization_id,
        contract_id=contract.id,
        code="A",
        budget=Decimal("100"),
        parent_id=root.id,
    )
    root.created_by_user_id = actor_user_id
    leaf.created_by_user_id = actor_user_id
    uow.contract_nodes.add_all([root, leaf])
    uow.contract_nodes.add_progress(
        ContractNodeProgress(
            id=uuid4(),
            organization_id=organization_id,
            contract_node_id=leaf.id,
            progress_date=snapshot_date,
            progress=Decimal("1.0"),
            created_at=utc_now(),
            created_by_user_id=actor_user_id,
            updated_at=None,
            updated_by_user_id=None,
        )
    )

    value_type = (
        ValueTypeBuilder()
        .with_organization_id(organization_id)
        .with_code("MAT")
        .with_direction(ValueDirection.COST)
        .build()
    )
    uow.value_types.add(value_type)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(organization_id)
        .with_reference("FV/E2E/1")
        .with_buyer_id(owner.id)
        .with_seller_id(supplier.id)
        .with_status(FinancialRecordStatus.IN_PROGRESS)
        .build()
    )
    uow.financial_records.add(record)

    line = (
        FinancialRecordLineBuilder()
        .with_organization_id(organization_id)
        .with_created_at(datetime.combine(snapshot_date, datetime.min.time()))
        .with_financial_record_id(record.id)
        .with_contract_id(contract.id)
        .with_contract_node_id(leaf.id)
        .with_value_type_id(value_type.id)
        .with_amount(Amount(Decimal("100"), VatRate.VAT_23))
        .build()
    )
    uow.financial_record_lines.add(organization_id=organization_id, line=line)

    document = (
        DocumentBuilder()
        .with_organization_id(organization_id)
        .with_document_source(DocumentSource.PDF)
        .with_file_path("incoming/doc-1.pdf")
        .with_parsed_payload({"ok": True})
        .build()
    )
    uow.documents.add(document)
    uow.documents.attach_to_record(
        organization_id=organization_id,
        document_id=document.id,
        record_id=record.id,
    )

    docs = services_memory.list_documents_query_service.execute(
        action=ListDocumentsQueryCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            has_payload=True,
            has_record=True,
            source=None,
        ),
        uow=uow,
    )
    assert len(docs) == 1
    assert docs[0].document_id == document.id
    assert docs[0].has_record is True

    snapshot, created = services_memory.create_contract_snapshot.execute(
        action=CreateContractSnapshotCommand(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            contract_id=contract.id,
            snapshot_date=snapshot_date,
        ),
        uow=uow,
    )
    assert created is True
    assert snapshot.contract_id == contract.id

    node_snapshots = uow.contract_node_snapshots.list_all()
    value_snapshots = uow.contract_node_value_snapshots.list_all()
    assert len(node_snapshots) >= 2
    assert len(value_snapshots) >= 1

    root_snapshot = next(s for s in node_snapshots if s.contract_node_id == root.id)
    assert root_snapshot.planned_budget == Decimal("100")
    assert root_snapshot.progress == Decimal("1")

    rows = services_memory.contract_cost_report.execute(
        action=GenerateContractCostReportQuery(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            contract_id=contract.id,
        ),
        uow=uow,
    )
    assert len(rows) == 1
    assert rows[0]["contract_code"] == "C-E2E-1"
    assert rows[0]["cost_node_code"] == "A"
    assert rows[0]["cost_type_code"] == "MAT"
    assert rows[0]["net_amount"] == Decimal("100")
    assert rows[0]["vat_amount"] == Decimal("23.00")
    assert rows[0]["gross_amount"] == Decimal("123.00")
