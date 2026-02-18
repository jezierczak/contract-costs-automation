from uuid import uuid4

from contract_costs.infrastructure.excel.excel_column import ExcelColumnType
from contract_costs.model.company import CompanyType
from contract_costs.services.companies.prepare.company_prepare_columns import (
    COMPANY_PREPARE_COLUMNS,
)
from contract_costs.services.companies.query.dto.company_dto import CompanyDTO


def _sample_company() -> CompanyDTO:
    return CompanyDTO(
        id=uuid4(),
        name="Company A",
        tax_number="1234567890",
        role=CompanyType.SUPPLIER,
        is_active=True,
        tags={"a", "b"},
        description="desc",
        address_street="Street 1",
        address_city="Krakow",
        address_zip_code="31-010",
        address_country="PL",
        phone_number="123456789",
        email="a@example.com",
        bank_account_number="123",
        bank_account_country_code="PL",
        iban="PL123",
    )


def test_company_prepare_columns_have_expected_metadata() -> None:
    assert COMPANY_PREPARE_COLUMNS[0].header == "ACTION"
    assert COMPANY_PREPARE_COLUMNS[0].column_type == ExcelColumnType.DROPDOWN
    assert COMPANY_PREPARE_COLUMNS[0].editable is True

    assert COMPANY_PREPARE_COLUMNS[1].header == "COMPANY_ID"
    assert COMPANY_PREPARE_COLUMNS[1].column_type == ExcelColumnType.HIDDEN


def test_company_prepare_columns_getters_return_expected_values() -> None:
    company = _sample_company()
    by_header = {c.header: c for c in COMPANY_PREPARE_COLUMNS}

    assert by_header["ACTION"].getter(company) == "none"
    assert by_header["COMPANY_ID"].getter(company) == str(company.id)
    assert by_header["Name"].getter(company) == "Company A"
    assert by_header["Tax Number"].getter(company) == "1234567890"
    assert by_header["Role"].getter(company) == "Supplier"

    tags_value = by_header["Tags"].getter(company)
    assert set(tags_value.split(",")) == {"a", "b"}

