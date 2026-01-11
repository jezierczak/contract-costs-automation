from contract_costs.infrastructure.excel.excel_column import (
    ExcelColumn,
    ExcelColumnType,
)
from contract_costs.services.contracts.prepare.dto.cost_node_prepare_dto import (
    CostNodePrepareDTO,
)

COST_NODE_PREPARE_COLUMNS: list[ExcelColumn[CostNodePrepareDTO]] = [

    # =====================
    # BUSINESS KEYS
    # =====================
    ExcelColumn("Code", lambda x: x.code),
    ExcelColumn("Name", lambda x: x.name),

    # =====================
    # TREE STRUCTURE
    # =====================
    ExcelColumn("Parent Code", lambda x: x.parent_code),

    # =====================
    # COST
    # =====================
    ExcelColumn("Budget", lambda x: x.budget),
    ExcelColumn("Quantity", lambda x: x.quantity),
    ExcelColumn("Unit", lambda x: x.unit),

    # =====================
    # WORKFLOW
    # =====================
    ExcelColumn(
        "Active",
        lambda x: x.is_active,
        ExcelColumnType.CHECKBOX,
        editable=True,
    ),
]
