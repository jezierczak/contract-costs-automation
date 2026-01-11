from contract_costs.infrastructure.excel.excel_column import ExcelColumn, ExcelColumnType
from contract_costs.model.company import CompanyType
from contract_costs.services.companies.apply.command import CompanyActionType
from contract_costs.services.companies.query.dto.company_dto import CompanyDTO

COMPANY_PREPARE_COLUMNS: list[ExcelColumn[CompanyDTO]] = [
    # =====================
    # WORKFLOW
    # =====================
    ExcelColumn(
        "ACTION",
        lambda _: "none",
        ExcelColumnType.DROPDOWN,
        editable=True,
        options=[r.value for r in CompanyActionType],
    ),

    # =====================
    # TECH
    # =====================
    ExcelColumn(
        "COMPANY_ID",
        lambda x: str(x.id),
        ExcelColumnType.HIDDEN,
    ),

    # =====================
    # BUSINESS KEYS
    # =====================
    ExcelColumn("Name", lambda x: x.name,editable=True),
    ExcelColumn("Tax Number", lambda x: x.tax_number,editable=True),
    ExcelColumn(
        "Role",
        lambda x: x.role.value,
        ExcelColumnType.DROPDOWN,
        editable=True,
        options=[r.value for r in CompanyType],
    ),

    # =====================
    # DESCRIPTION
    # =====================
    ExcelColumn("Description", lambda x: x.description,editable=True),

    # =====================
    # ADDRESS
    # =====================
    ExcelColumn("Street", lambda x: x.address_street,editable=True),
    ExcelColumn("City", lambda x: x.address_city,editable=True),
    ExcelColumn("Zip Code", lambda x: x.address_zip_code,editable=True),
    ExcelColumn("Country", lambda x: x.address_country,editable=True),

    # =====================
    # CONTACT
    # =====================
    ExcelColumn("Phone", lambda x: x.phone_number,editable=True),
    ExcelColumn("Email", lambda x: x.email,editable=True),

    # =====================
    # BANK
    # =====================
    ExcelColumn("Bank Account", lambda x: x.bank_account_number,editable=True),
    ExcelColumn("Bank Country", lambda x: x.bank_account_country_code,editable=True),

    # =====================
    # TAGS
    # =====================
    ExcelColumn("Tags", lambda x: ",".join(x.tags) if x.tags else "",editable=True),
]
