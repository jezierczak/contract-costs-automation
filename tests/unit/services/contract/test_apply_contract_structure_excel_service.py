import pytest
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from unittest.mock import MagicMock

from contract_costs.model.company import CompanyType
from contract_costs.model.contract import ContractStatus
from contract_costs.model.contract_node import ContractNodeInput
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.contracts.apply.apply_contract_structure_excel import ApplyContractStructureExcelService

from contract_costs.services.contracts.dto.create_contract_command import (
    CreateContractCommand,
)
from contract_costs.services.contracts.apply.command.update_contract_structure_command import (
    UpdateContractStructureCommand,
)


def make_contract_row():
    return [{
        "Name": "Test Contract",
        "Code": "C-1",
        "Description": "Desc",
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
        }
    ]


def test_apply_new_calls_create_service(monkeypatch):
    create_service = MagicMock()
    update_service = MagicMock()
    company_eval = MagicMock()

    company_eval.evaluate_from_tax.return_value = MagicMock()

    service = ApplyContractStructureExcelService(
        create_contract_service=create_service,
        update_contract_structure_service=update_service,
        company_evaluate_orchestrator=company_eval,
    )

    # Mock ExcelLoader
    monkeypatch.setattr(
        "contract_costs.infrastructure.excel.excel_loader.ExcelLoader.load",
        lambda **kwargs: make_contract_row()
        if kwargs["sheet_name"] == service.CONTRACT_SHEET
        else make_node_rows(),
    )

    service.apply_new(
        excel_path=Path("fake.xlsx"),
        organization_id=uuid4(),
        actor_user_id=uuid4(),
    )

    assert create_service.init.called
    assert create_service.add_contract_node_tree.called
    assert create_service.execute.called
    assert not update_service.execute.called


def test_apply_update_calls_update_service(monkeypatch):
    create_service = MagicMock()
    update_service = MagicMock()
    company_eval = MagicMock()

    company_eval.evaluate_from_tax.return_value = MagicMock()

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

    contract_id = uuid4()

    service.apply_update(
        excel_path=Path("fake.xlsx"),
        contract_id=contract_id,
        organization_id=uuid4(),
        actor_user_id=uuid4(),
    )

    assert update_service.execute.called
    command = update_service.execute.call_args[0][0]

    assert isinstance(command, UpdateContractStructureCommand)
    assert command.contract_id == contract_id
    assert len(command.contract_node_input) == 1
    assert not create_service.init.called


def test_build_contract_node_tree_duplicate_code_raises():
    rows = [
        {"Code": "A", "Name": "A", "Budget": 10, "Quantity": None, "Unit": None, "Parent Code": None},
        {"Code": "A", "Name": "A2", "Budget": 20, "Quantity": None, "Unit": None, "Parent Code": None},
    ]

    with pytest.raises(ValueError):
        ApplyContractStructureExcelService._build_contract_node_tree(rows)


def test_build_contract_node_tree_invalid_parent_raises():
    rows = [
        {"Code": "A", "Name": "A", "Budget": 10, "Quantity": None, "Unit": None, "Parent Code": "X"},
    ]

    with pytest.raises(ValueError):
        ApplyContractStructureExcelService._build_contract_node_tree(rows)


def test_build_contract_node_tree_multiple_roots_creates_root():
    rows = [
        {"Code": "A", "Name": "A", "Budget": 10, "Quantity": None, "Unit": None, "Parent Code": None},
        {"Code": "B", "Name": "B", "Budget": 20, "Quantity": None, "Unit": None, "Parent Code": None},
    ]

    result = ApplyContractStructureExcelService._build_contract_node_tree(rows)

    assert len(result) == 1
    assert result[0]["code"] == "ROOT"
    assert len(result[0]["children"]) == 2


def test_map_unit_invalid():
    with pytest.raises(ValueError):
        ApplyContractStructureExcelService._map_unit("INVALID")
