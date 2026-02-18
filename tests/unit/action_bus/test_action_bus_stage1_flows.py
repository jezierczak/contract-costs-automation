from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest

from contract_costs.action_bus.action_bus import ActionBus
from contract_costs.action_bus.permission_resolver import PermissionResolver
from contract_costs.action_bus.permission_validator import PermissionValidator
from contract_costs.model.amount import Amount, VatRate
from contract_costs.model.company import CompanyType
from contract_costs.model.company import CompanyType as CompanyRole
from contract_costs.model.contract import ContractStatus, ContractType
from contract_costs.model.document import DocumentSource
from contract_costs.model.financial_record import FinancialRecordStatus, PaymentMethod, PaymentStatus
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.companies.apply.command import (
    ApplyCompaniesCommand,
    ApplyCompanyCommand,
    CompanyActionType,
)
from contract_costs.services.contracts.apply.apply_contract_progress_excel_service import (
    ApplyContractProgressExcelService,
)
from contract_costs.services.contracts.apply.apply_contract_progress_service import (
    ApplyContractProgressService,
)
from contract_costs.services.contracts.apply.apply_contract_structure_excel import (
    ApplyContractStructureExcelService,
)
from contract_costs.services.contracts.apply.command.apply_contract_progress_excel_command import (
    ApplyContractProgressExcelCommand,
)
from contract_costs.services.contracts.apply.command.apply_contract_structure_excel_command import (
    ApplyNewContractStructureExcelCommand,
)
from contract_costs.services.contracts.apply.update_contract_structure_service import (
    UpdateContractStructureService,
)
from contract_costs.services.contracts.builders.contract_node_tree_builder import (
    DefaultContractNodeTreeBuilder,
)
from contract_costs.services.contracts.create_contract_service import CreateContractService
from contract_costs.services.contracts.validators.contract_node_tree_validator import (
    ContractNodeEntityValidator,
)
from contract_costs.services.documents.apply.dto.apply_document_command import (
    ApplyDocumentCommand,
    DocumentApplyAction,
)
from contract_costs.services.financial_records.actions.dto.invoice_action_command import (
    FinancialRecordAction,
    FinancialRecordActionCommand,
    FinancialRecordSelector,
)
from contract_costs.services.financial_records.assigment.apply.commands.apply_invoice_excel_bach_command import (
    ApplyInvoiceExcelBatchCommand,
)
from contract_costs.services.financial_records.assigment.apply.commands.invoice_command import (
    InvoiceCommand,
)
from contract_costs.services.financial_records.assigment.invoice_sources.dto.common import (
    FinancialRecordLineUpdate,
    FinancialRecordUpdate,
    InvoiceExcelBatch,
)
from tests.builders.company_builder import CompanyBuilder
from tests.builders.contract_builder import ContractBuilder
from tests.builders.document_builder import DocumentBuilder
from tests.builders.financial_record_builder import FinancialRecordBuilder
from tests.helpers.contracts_helpers import make_contract_node


class _AllowAllResolver(PermissionResolver):
    def has_permission(self, *, organization_id, user_id, action_type) -> bool:
        return True


def _bus_for_uow(uow):
    validator = PermissionValidator(permission_resolver=_AllowAllResolver())
    return ActionBus(permission_validator=validator, uow_factory=lambda: uow)


def test_action_bus_apply_contract_structure_creates_contract(monkeypatch, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    builder = DefaultContractNodeTreeBuilder()
    validator = ContractNodeEntityValidator()
    company_eval = pytest.MonkeyPatch()
    company_eval = type("Eval", (), {})()
    company_eval.evaluate_from_tax = lambda **kwargs: (
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyRole.OWN)
        .build()
    )

    handler = ApplyContractStructureExcelService(
        create_contract_service=CreateContractService(
            contract_node_tree_builder=builder,
            contract_node_tree_validator=validator,
        ),
        update_contract_structure_service=UpdateContractStructureService(
            contract_node_tree_builder=builder,
            contract_node_tree_validator=validator,
        ),
        company_evaluate_orchestrator=company_eval,
    )

    contract_row = [{
        "Name": "AB Contract",
        "Code": "AB-1",
        "Description": None,
        "Owner NIP": "6762680195",
        "Client NIP": None,
        "Start Date": None,
        "End Date": None,
        "Budget": 1000,
        "Path": None,
        "Status": "ACTIVE",
    }]
    node_rows = [{
        "Code": "A",
        "Name": "Node A",
        "Budget": 100,
        "Quantity": None,
        "Unit": None,
        "Parent Code": None,
        "Active": True,
    }]

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: contract_row if kwargs["sheet_name"] == handler.CONTRACT_SHEET else node_rows,
    )

    bus.execute(
        action=ApplyNewContractStructureExcelCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            excel_path=Path("fake.xlsx"),
        ),
        handler=handler,
    )

    contracts = uow.contracts.list_contracts(org_id, contract_type=ContractType.PROJECT)
    nodes = uow.contract_nodes.list_nodes(organization_id=org_id)
    assert len(contracts) == 1
    assert contracts[0].code == "AB-1"
    assert any(n.code == "A" for n in nodes)


def test_action_bus_apply_contract_progress_updates_node(monkeypatch, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    contract = (
        ContractBuilder()
        .with_organization_id(org_id)
        .with_owner(CompanyBuilder().with_role(CompanyType.OWN).build())
        .with_status(ContractStatus.ACTIVE)
        .build()
    )
    uow.contracts.add(contract)

    node = make_contract_node(organization_id=org_id, contract_id=contract.id, code="A")
    uow.contract_nodes.add_all([node])

    handler = ApplyContractProgressExcelService(
        apply_contract_progress_service=ApplyContractProgressService(id_generator=uuid4)
    )

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: [{
            "Contract": contract.code,
            "Node ID": str(node.id),
            "New Progress [%]": Decimal("50"),
            "Code": node.code,
        }],
    )

    bus.execute(
        action=ApplyContractProgressExcelCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            contract_id=contract.id,
            excel_path=Path("fake.xlsx"),
        ),
        handler=handler,
    )

    updated = uow.contract_nodes.get(organization_id=org_id, contract_node_id=node.id)
    assert updated is not None
    assert updated.progress == Decimal("0.5")


def test_action_bus_apply_document_create_new_creates_record_and_links_document(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    payload = {
        "buyer": {"role": "Buyer", "tax_number": "6762680195", "name": "Buyer Co"},
        "seller": {"role": "Seller", "tax_number": "6792740424", "name": "Seller Co"},
        "record": {
            "reference": "DOC-1",
            "invoice_date": "2026-02-16",
            "selling_date": "2026-02-16",
            "payment_method": "cash",
            "payment_status": "unknown",
        },
        "lines": [],
        "document_type": "invoice",
    }
    document = (
        DocumentBuilder()
        .with_organization_id(org_id)
        .with_document_source(DocumentSource.PDF)
        .with_parsed_payload(payload)
        .build()
    )
    uow.documents.add(document)

    bus.execute(
        action=ApplyDocumentCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            document_id=document.id,
            action=DocumentApplyAction.CREATE_NEW,
        ),
        handler=services_memory.apply_document_service,
    )

    updated_document = uow.documents.get(organization_id=org_id, document_id=document.id)
    records = uow.financial_records.list_all(organization_id=org_id)
    assert updated_document is not None
    assert updated_document.financial_record_id is not None
    assert len(records) == 1
    assert records[0].reference == "DOC-1"


def test_action_bus_apply_financial_records_batch_creates_record(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)
    uow.companies.add(
        CompanyBuilder()
        .with_organization_id(org_id)
        .with_role(CompanyType.OWN)
        .with_tax_number("6762680195")
        .with_name("Own Company")
        .build()
    )

    batch = InvoiceExcelBatch(
        financial_records=[
            FinancialRecordUpdate(
                command=InvoiceCommand.APPLY,
                reference="FR-1",
                record_id=None,
                old_reference=None,
                invoice_date=date(2026, 2, 16),
                selling_date=date(2026, 2, 16),
                buyer_tax_number="6762680195",
                seller_tax_number="6792740424",
                payment_method=PaymentMethod.CASH,
                due_date=None,
                paid_date=None,
                tags=None,
                payment_status=PaymentStatus.UNKNOWN,
                status=FinancialRecordStatus.IN_PROGRESS,
            )
        ],
        lines=[
            FinancialRecordLineUpdate(
                record_line_id=None,
                record_reference="FR-1",
                item_name="Item 1",
                description=None,
                quantity=Decimal("1"),
                unit=UnitOfMeasure.PIECE,
                amount=Amount(value=Decimal("100"), vat_rate=VatRate.VAT_23),
                contract_code=None,
                contract_node_code=None,
                value_type_code=None,
                agreement_code=None,
                agreement_node_code=None,
            )
        ],
        buyers=[],
        sellers=[],
    )

    bus.execute(
        action=ApplyInvoiceExcelBatchCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            batch=batch,
        ),
        handler=services_memory.apply_financial_record_excel_batch,
    )

    records = uow.financial_records.get_by_reference(
        organization_id=org_id,
        reference="FR-1",
    )
    assert len(records) == 1
    lines = uow.financial_record_lines.list_by_financial_record(
        organization_id=org_id,
        financial_record_id=records[0].id,
    )
    assert len(lines) == 1
    assert lines[0].item_name == "Item 1"


def test_action_bus_financial_records_paid_marks_record_paid(uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    record = (
        FinancialRecordBuilder()
        .with_organization_id(org_id)
        .with_reference("PAY-1")
        .with_payment_status(PaymentStatus.UNPAID)
        .build()
    )
    uow.financial_records.add(record)

    bus.execute(
        action=FinancialRecordActionCommand(
            organization_id=org_id,
            actor_user_id=user_id,
            action=FinancialRecordAction.MARK_PAID,
            selectors=[FinancialRecordSelector(record_reference="PAY-1")],
            payload={"paid_at": date(2026, 2, 17)},
        ),
        handler=services_memory_financial_record_action_handler(),
    )

    updated = uow.financial_records.get(organization_id=org_id, record_id=record.id)
    assert updated is not None
    assert updated.payment_status == PaymentStatus.PAID
    assert updated.paid_date == date(2026, 2, 17)


def services_memory_financial_record_action_handler():
    from contract_costs.services.financial_records.actions.financial_record_action_service import (
        FinancialRecordActionService,
    )

    return FinancialRecordActionService()


def test_action_bus_apply_companies_command_executes_when_action_type_is_present(services_memory, uow):
    org_id = uuid4()
    user_id = uuid4()
    bus = _bus_for_uow(uow)

    action = ApplyCompaniesCommand(
        organization_id=org_id,
        actor_user_id=user_id,
        commands=[
            ApplyCompanyCommand(
                organization_id=org_id,
                actor_user_id=user_id,
                apply_action_type=CompanyActionType.CREATE,
                company_id=None,
                tax_number="1234567890",
                name="Supplier X",
                role=CompanyType.SUPPLIER,
                description=None,
                address_street=None,
                address_city=None,
                address_zip_code=None,
                address_country=None,
                phone_number=None,
                email=None,
                bank_account_number=None,
                bank_account_country_code=None,
                tags=set(),
            )
        ],
    )

    bus.execute(action=action, handler=services_memory.apply_companies_from_excel_service)

    created = uow.companies.get_by_tax_number(organization_id=org_id, tax_number="1234567890")
    assert created is not None
    assert created.name == "Supplier X"
