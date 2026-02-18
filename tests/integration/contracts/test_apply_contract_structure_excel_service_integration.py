from pathlib import Path
from unittest.mock import MagicMock
from uuid import uuid4

from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractStatus, ContractType
from contract_costs.services.contracts.apply.apply_contract_structure_excel import (
    ApplyContractStructureExcelService,
)
from contract_costs.services.contracts.apply.command.apply_contract_structure_excel_command import (
    ApplyNewContractStructureExcelCommand,
    UpdateContractStructureExcelCommand,
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
from tests.builders.company_builder import CompanyBuilder


def make_contract_row():
    return [{
        "Name": "Integration Contract",
        "Code": "C-100",
        "Description": "Integration test",
        "Owner NIP": "123",
        "Client NIP": None,
        "Start Date": None,
        "End Date": None,
        "Budget": 1000,
        "Path": None,
        "Status": "ACTIVE",
    }]


def make_node_rows():
    return [
        {
            "Code": "A",
            "Name": "Node A",
            "Budget": 100,
            "Quantity": None,
            "Unit": None,
            "Parent Code": None,
            "Active": True,
        },
        {
            "Code": "B",
            "Name": "Node B",
            "Budget": 200,
            "Quantity": None,
            "Unit": None,
            "Parent Code": "A",
            "Active": True,
        },
    ]


def test_integration_apply_new_creates_contract_with_tree(monkeypatch, contract_repo, contract_node_repo, uow):
    builder = DefaultContractNodeTreeBuilder()
    validator = ContractNodeEntityValidator()

    create_service = CreateContractService(
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    update_service = UpdateContractStructureService(
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    organization_id = uuid4()
    actor_user_id = uuid4()

    company_eval = MagicMock()
    company_eval.evaluate_from_tax.return_value = (
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.BUYER)
        .build()
    )

    service = ApplyContractStructureExcelService(
        create_contract_service=create_service,
        update_contract_structure_service=update_service,
        company_evaluate_orchestrator=company_eval,
    )

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: make_contract_row()
        if kwargs["sheet_name"] == service.CONTRACT_SHEET
        else make_node_rows(),
    )

    service.execute(
        action=ApplyNewContractStructureExcelCommand(
            excel_path=Path("fake.xlsx"),
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        ),
        uow=uow,
    )

    contracts = contract_repo.list_contracts(organization_id, contract_type=ContractType.PROJECT)
    assert len(contracts) == 1

    contract = contracts[0]
    assert contract.code == "C-100"
    assert contract.status == ContractStatus.ACTIVE

    nodes = contract_node_repo.list_nodes(organization_id=organization_id)
    codes = {n.code for n in nodes}
    assert "ROOT" in codes
    assert "A" in codes
    assert "B" in codes


def test_integration_apply_update_replaces_structure(monkeypatch, contract_repo, contract_node_repo, uow):
    builder = DefaultContractNodeTreeBuilder()
    validator = ContractNodeEntityValidator()

    create_service = CreateContractService(
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    update_service = UpdateContractStructureService(
        contract_node_tree_builder=builder,
        contract_node_tree_validator=validator,
    )

    organization_id = uuid4()
    actor_user_id = uuid4()

    company_eval = MagicMock()
    company_eval.evaluate_from_tax.return_value = (
        CompanyBuilder()
        .with_organization_id(organization_id)
        .with_role(CompanyType.BUYER)
        .build()
    )

    service = ApplyContractStructureExcelService(
        create_contract_service=create_service,
        update_contract_structure_service=update_service,
        company_evaluate_orchestrator=company_eval,
    )

    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: make_contract_row()
        if kwargs["sheet_name"] == service.CONTRACT_SHEET
        else make_node_rows(),
    )

    service.execute(
        action=ApplyNewContractStructureExcelCommand(
            excel_path=Path("fake.xlsx"),
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        ),
        uow=uow,
    )

    contract = contract_repo.list_contracts(organization_id, contract_type=ContractType.PROJECT)[0]

    service.execute(
        action=UpdateContractStructureExcelCommand(
            excel_path=Path("fake.xlsx"),
            contract_id=contract.id,
            organization_id=organization_id,
            actor_user_id=actor_user_id,
        ),
        uow=uow,
    )

    nodes = contract_node_repo.list_nodes(organization_id=organization_id)
    assert len(nodes) >= 2
    assert any(n.code == "A" for n in nodes)
