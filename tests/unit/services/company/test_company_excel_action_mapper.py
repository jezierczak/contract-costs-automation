from uuid import uuid4

import pytest

from contract_costs.services.companies.apply.adapters.company_excel_action_mapper import (
    CompanyExcelActionMapper,
)
from contract_costs.services.companies.apply.command import CompanyActionType


def test_company_excel_action_mapper_maps_row_to_command_domain_contract() -> None:
    org_id = uuid4()
    user_id = uuid4()
    row = {
        "ACTION": "create",
        "COMPANY_ID": str(uuid4()),
        "Tax Number": "1234567890",
        "Name": "Test Supplier",
        "Role": "Supplier",
        "Tags": "a, b, ,c",
    }

    command = CompanyExcelActionMapper.map(
        organization_id=org_id,
        actor_user_id=user_id,
        row=row,
    )
    assert command.tax_number == "1234567890"
    assert command.name == "Test Supplier"
    assert command.apply_action_type == CompanyActionType.CREATE
    assert command.organization_id == org_id
    assert command.actor_user_id == user_id
    assert command.tags == {"a", "b", "c"}


def test_company_excel_action_mapper_defaults_action_to_none() -> None:
    row = {
        "COMPANY_ID": "",
        "Tax Number": "1234567890",
        "Name": "Test Supplier",
        "Role": "Supplier",
    }

    command = CompanyExcelActionMapper.map(
        organization_id=uuid4(),
        actor_user_id=uuid4(),
        row=row,
    )

    assert command.apply_action_type == CompanyActionType.NONE
    assert command.company_id is None


def test_company_excel_action_mapper_rejects_invalid_action() -> None:
    row = {
        "ACTION": "bad",
        "COMPANY_ID": "",
        "Tax Number": "1234567890",
        "Name": "Test Supplier",
        "Role": "Supplier",
    }

    with pytest.raises(ValueError):
        CompanyExcelActionMapper.map(
            organization_id=uuid4(),
            actor_user_id=uuid4(),
            row=row,
        )


def test_company_excel_action_mapper_rejects_invalid_role() -> None:
    row = {
        "ACTION": "create",
        "COMPANY_ID": "",
        "Tax Number": "1234567890",
        "Name": "Test Supplier",
        "Role": "BadRole",
    }

    with pytest.raises(ValueError):
        CompanyExcelActionMapper.map(
            organization_id=uuid4(),
            actor_user_id=uuid4(),
            row=row,
        )
