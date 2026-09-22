from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.builders.financial_record_line_builder import FinancialRecordLineBuilder
from tests.builders.value_type_builder import ValueTypeBuilder
from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractType
from contract_costs.model.financial_record import FinancialRecordStatus
from contract_costs.services.financial_records.assigment.prepare.dto.generatr_financial_redcord_assignment_bundle_command import (
    GenerateFinancialRecordAssignmentBundleCommand,
)
from contract_costs.services.financial_records.assigment.prepare.generate_assignment_bundle_service import (
    GenerateFinancialRecordAssignmentBundleService,
)


def test_generate_assignment_bundle_service_builds_domain_bundle_and_updates_status() -> None:
    org_id = uuid4()
    user_id = uuid4()

    owner = CompanyBuilder().with_role(CompanyType.OWN).with_name("Owner").with_tax_number("111").build()
    supplier = CompanyBuilder().with_role(CompanyType.SUPPLIER).with_name("Supplier").with_tax_number("222").build()
    other_own = CompanyBuilder().with_role(CompanyType.OWN).with_name("Other Own").with_tax_number("333").build()

    project = ContractBuilder().with_id(uuid4()).with_code("P-1").with_contract_type(ContractType.PROJECT).build()
    system = ContractBuilder().with_id(uuid4()).with_code("S-1").with_contract_type(ContractType.SYSTEM).build()
    agreement = ContractBuilder().with_id(uuid4()).with_code("A-1").with_contract_type(ContractType.AGREEMENT).build()

    project_node = SimpleNamespace(
        id=uuid4(),
        contract_id=project.id,
        parent_id=None,
        code="PN-1",
        name="Project Node",
        budget=Decimal("1000"),
    )
    agreement_node = SimpleNamespace(
        id=uuid4(),
        contract_id=agreement.id,
        parent_id=None,
        code="AN-1",
        name="Agreement Node",
        budget=Decimal("500"),
    )

    value_type = ValueTypeBuilder().with_code("VT-1").build()

    doc = DocumentBuilder().with_file_path("incoming/documents/fv1.pdf").build()
    rec_new = (
        FinancialRecordBuilder()
        .with_id(uuid4())
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.NEW_COST)
        .with_reference("FV/1")
        .with_buyer_id(owner.id)
        .with_seller_id(supplier.id)
        .with_documents([doc])
        .with_tags({"t1"})
        .build()
    )
    rec_in_progress = (
        FinancialRecordBuilder()
        .with_id(uuid4())
        .with_organization_id(org_id)
        .with_status(FinancialRecordStatus.IN_PROGRESS)
        .with_reference("FV/2")
        .with_buyer_id(owner.id)
        .with_seller_id(supplier.id)
        .build()
    )

    line_assigned = (
        FinancialRecordLineBuilder()
        .with_id(uuid4())
        .with_financial_record_id(rec_new.id)
        .with_contract_id(project.id)
        .with_contract_node_id(project_node.id)
        .with_value_type_id(value_type.id)
        .build()
    )
    line_unassigned = (
        FinancialRecordLineBuilder()
        .with_id(uuid4())
        .with_financial_record_id(None)
        .build()
    )

    record_repo = SimpleNamespace(
        get_for_assignment=lambda **_: [rec_new, rec_in_progress],
        update=Mock(),
    )
    line_repo = SimpleNamespace(
        list_by_financial_record_ids=lambda **_: [line_assigned],
        list_unassigned=lambda **_: [line_unassigned],
    )
    company_repo = SimpleNamespace(
        get_owners=lambda **_: [owner],
        list_all=lambda **_: [owner, supplier, other_own],
        get=lambda **kwargs: owner if kwargs["company_id"] == owner.id else supplier,
    )
    contract_repo = SimpleNamespace(
        list_all_by_type=lambda **kwargs: (
            [project] if kwargs["contract_type"] == ContractType.PROJECT
            else [system] if kwargs["contract_type"] == ContractType.SYSTEM
            else [agreement]
        )
    )
    contract_node_repo = SimpleNamespace(
        list_leaf_nodes_for_active_contracts=lambda **_: [project_node, agreement_node]
    )
    value_type_repo = SimpleNamespace(list_all=lambda **_: [value_type])

    uow = SimpleNamespace(
        financial_records=record_repo,
        financial_record_lines=line_repo,
        companies=company_repo,
        contracts=contract_repo,
        contract_nodes=contract_node_repo,
        value_types=value_type_repo,
    )
    action = GenerateFinancialRecordAssignmentBundleCommand(
        organization_id=org_id,
        actor_user_id=user_id,
        invoice_status=FinancialRecordStatus.NEW_COST,
    )

    service = GenerateFinancialRecordAssignmentBundleService(clock=lambda: rec_new.created_at)
    bundle = service.execute(action=action, uow=uow)

    assert record_repo.update.call_count == 1
    assert len(bundle.records) == 2
    assert len(bundle.record_lines) == 2
    assert len(bundle.buyers) == 1
    assert len(bundle.sellers) == 1
    assert bundle.sellers[0].tax_number == "222"
    assert len(bundle.project_contracts) == 2
    assert len(bundle.agreement_contracts) == 1
    assert len(bundle.project_contract_nodes) == 1
    assert len(bundle.agreement_contract_nodes) == 1
    assert bundle.records[0].status == FinancialRecordStatus.IN_PROGRESS
    assert bundle.records[0].primary_document_path == "incoming/documents/fv1.pdf"
    assert bundle.record_lines[0].record_reference == "FV/1"
    assert bundle.record_lines[1].record_reference == ""


def test_generate_assignment_bundle_service_raises_when_contract_code_missing() -> None:
    org_id = uuid4()
    user_id = uuid4()
    owner = CompanyBuilder().with_role(CompanyType.OWN).build()
    supplier = CompanyBuilder().with_role(CompanyType.SUPPLIER).build()
    rec = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_buyer_id(owner.id)
        .with_seller_id(supplier.id)
        .with_status(FinancialRecordStatus.NEW_COST)
        .build()
    )
    unknown_contract_id = uuid4()
    bad_node = SimpleNamespace(
        id=uuid4(),
        contract_id=unknown_contract_id,
        parent_id=None,
        code="X",
        name="X",
        budget=Decimal("1"),
    )

    uow = SimpleNamespace(
        financial_records=SimpleNamespace(get_for_assignment=lambda **_: [rec], update=Mock()),
        financial_record_lines=SimpleNamespace(list_by_financial_record_ids=lambda **_: [], list_unassigned=lambda **_: []),
        companies=SimpleNamespace(
            get_owners=lambda **_: [owner],
            list_all=lambda **_: [owner, supplier],
            get=lambda **kwargs: owner if kwargs["company_id"] == owner.id else supplier,
        ),
        contracts=SimpleNamespace(list_all_by_type=lambda **_: []),
        contract_nodes=SimpleNamespace(list_leaf_nodes_for_active_contracts=lambda **_: [bad_node]),
        value_types=SimpleNamespace(list_all=lambda **_: []),
    )
    action = GenerateFinancialRecordAssignmentBundleCommand(
        organization_id=org_id,
        actor_user_id=user_id,
        invoice_status=FinancialRecordStatus.NEW_COST,
    )

    with pytest.raises(RuntimeError, match="Missing contract code"):
        GenerateFinancialRecordAssignmentBundleService().execute(action=action, uow=uow)
