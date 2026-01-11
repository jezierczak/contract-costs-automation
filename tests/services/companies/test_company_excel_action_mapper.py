from uuid import uuid4

import pytest


from contract_costs.model.company import CompanyType
from contract_costs.services.companies.apply.adapters.company_excel_action_mapper import CompanyExcelActionMapper
from contract_costs.services.companies.apply.command import CompanyActionCommand, CompanyActionType


@pytest.fixture
def base_row() -> dict:
    return {
        "ACTION": "update",
        "COMPANY_ID": str(uuid4()),
        "Name": "Company A",
        "Tax Number": "1234567890",
        "Role": CompanyType.SUPPLIER.value,
        "Description": "Desc",
        "Street": "Street",
        "City": "City",
        "Zip Code": "00-000",
        "Country": "PL",
        "Phone": "123",
        "Email": "a@b.com",
        "Bank Account": "12345678901234567890123456",
        "Bank Country": "PL",
        "Tags": "a, b ,c",
    }

def test_mapper_happy_path(base_row):
    cmd = CompanyExcelActionMapper.map(base_row)

    assert isinstance(cmd, CompanyActionCommand)
    assert cmd.action == CompanyActionType.UPDATE
    assert cmd.company_id is not None
    assert cmd.name == "Company A"
    assert cmd.tax_number == "1234567890"
    assert cmd.role == CompanyType.SUPPLIER
    assert cmd.description == "Desc"
    assert cmd.address_city == "City"
    assert cmd.phone_number == "123"
    assert cmd.email == "a@b.com"
    assert cmd.tags == {"a", "b", "c"}

def test_mapper_without_company_id_creates_none(base_row):
    base_row["COMPANY_ID"] = None

    cmd = CompanyExcelActionMapper.map(base_row)

    assert cmd.company_id is None

def test_mapper_action_none_when_empty(base_row):
    base_row["ACTION"] = None

    cmd = CompanyExcelActionMapper.map(base_row)

    assert cmd.action == CompanyActionType.NONE

def test_mapper_invalid_role_raises(base_row):
    base_row["Role"] = "NOT_A_ROLE"

    with pytest.raises(ValueError):
        CompanyExcelActionMapper.map(base_row)

def test_mapper_invalid_action_raises(base_row):
    base_row["ACTION"] = "explode"

    with pytest.raises(ValueError):
        CompanyExcelActionMapper.map(base_row)

def test_mapper_empty_tags(base_row):
    base_row["Tags"] = ""

    cmd = CompanyExcelActionMapper.map(base_row)

    assert cmd.tags == set()
