from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.services.companies.query.dto.company_dto import CompanyDTO


def company_list_columns() -> list[ExcelColumn[CompanyDTO]]:
    return ExcelColumn.from_lists(
        headers=[
            "Q",
            "NAME",
            "NIP",
            "ROLE",
            "CITY",
            "BANK ACCOUNT",
            "PHONE",
            "EMAIL",
        ],
        getters=[
            lambda c: str(c.quality_score) if c.quality_score is not None else "-",
            lambda c: c.name,
            lambda c: c.tax_number,
            lambda c: c.role.value,
            lambda c: c.address_city or "-",
            lambda c: c.bank_account_number or "-",
            lambda c: c.phone_number or "-",
            lambda c: c.email or "-"
        ],
        types=[
            ExcelColumnType.DISPLAY,  # Q
            ExcelColumnType.DISPLAY,  # name
            ExcelColumnType.DISPLAY,  # nip
            ExcelColumnType.DISPLAY,  # role
            ExcelColumnType.DISPLAY,  # city
            ExcelColumnType.DISPLAY,  # bank
            ExcelColumnType.DISPLAY,  # phone
            ExcelColumnType.DISPLAY,  # email
        ],
    )
