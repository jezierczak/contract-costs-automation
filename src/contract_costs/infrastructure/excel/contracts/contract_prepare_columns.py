from contract_costs.infrastructure.excel.excel_column import (
    ExcelColumn,
    ExcelColumnType,
)
from contract_costs.services.contracts.prepare.dto.contract_prepare_dto import (
    ContractPrepareDTO,
)

CONTRACT_PREPARE_COLUMNS: list[ExcelColumn[ContractPrepareDTO]] = [

    # =====================
    # BUSINESS KEYS
    # =====================
    ExcelColumn("Code", lambda x: x.code, editable=False),
    ExcelColumn("Name", lambda x: x.name, editable=True),

    # =====================
    # PARTIES
    # =====================
    ExcelColumn("Owner NIP", lambda x: x.owner_nip, editable=False),
    ExcelColumn("Client NIP", lambda x: x.client_nip, editable=True),

    # =====================
    # DESCRIPTION
    # =====================
    ExcelColumn("Description", lambda x: x.description, editable=True),

    # =====================
    # DATES
    # =====================
    ExcelColumn("Start Date", lambda x: x.start_date, editable=True),
    ExcelColumn("End Date", lambda x: x.end_date, editable=True),

    # =====================
    # FINANCE
    # =====================
    ExcelColumn("Budget", lambda x: x.budget, editable=True),

    # =====================
    # TECH / META
    # =====================
    ExcelColumn("Path", lambda x: x.path, editable=False),

    ExcelColumn(
        "Status",
        lambda x: x.status,
        ExcelColumnType.DROPDOWN,
        editable=True,
        options=["PLANNED", "ACTIVE", "FINISHED", "CANCELLED"],
    )
]
