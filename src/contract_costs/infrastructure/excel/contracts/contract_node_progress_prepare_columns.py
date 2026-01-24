from contract_costs.infrastructure.excel.excel_column import (
    ExcelColumn,
    ExcelColumnType,
)
from contract_costs.services.contracts.prepare.dto.contract_node_progress_prepare_dto import (
    ContractNodeProgressPrepareDTO,
)

CONTRACT_NODE_PROGRESS_PREPARE_COLUMNS: list[
    ExcelColumn[ContractNodeProgressPrepareDTO]
] = [
    ExcelColumn(
        "Node ID",
        lambda x: str(x.contract_node_id),
        ExcelColumnType.HIDDEN,
        editable=False,
    ),
    # =====================
    # BUSINESS CONTEXT
    # =====================
    ExcelColumn(
        "Contract",
        lambda x: x.contract_code,
        editable=False,
    ),

    # =====================
    # BUSINESS KEYS
    # =====================
    ExcelColumn(
        "Code",
        lambda x: x.code,
        editable=False,
    ),
    ExcelColumn(
        "Name",
        lambda x: x.name,
        editable=False,
    ),

    # =====================
    # CONTEXT (READ-ONLY)
    # =====================
    ExcelColumn(
        "Budget",
        lambda x: x.budget,
        editable=False,
    ),

    # =====================
    # PROGRESS (READ / WRITE)
    # =====================
    ExcelColumn(
        "Current Progress [%]",
        lambda x: x.current_progress_percent,
        ExcelColumnType.PERCENT,
        editable=False,
    ),
    ExcelColumn(
        "New Progress [%]",
        lambda x: x.new_progress_percent,
        ExcelColumnType.PERCENT,
        editable=True,
    ),

    # =====================
    # WORKFLOW
    # =====================
    ExcelColumn(
        "Active",
        lambda x: x.is_active,
        ExcelColumnType.CHECKBOX,
        editable=False,
    ),
]
