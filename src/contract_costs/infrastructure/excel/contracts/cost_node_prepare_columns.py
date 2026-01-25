from contract_costs.infrastructure.excel.excel_column import (
    ExcelColumn,
    ExcelColumnType,
)
from contract_costs.model.unit_of_measure import UnitOfMeasure
from contract_costs.services.contracts.prepare.dto.contract_node_prepare_dto import (
    ContractNodePrepareDTO,
)

CONTRACT_NODE_PREPARE_COLUMNS: list[ExcelColumn[ContractNodePrepareDTO]] = [

    # =====================
    # BUSINESS KEYS
    # =====================
    ExcelColumn("Code", lambda x: x.code, editable=True),
    ExcelColumn("Name", lambda x: x.name, editable=True),

    # =====================
    # TREE STRUCTURE
    # =====================
    ExcelColumn("Parent Code", lambda x: x.parent_code, editable=True),

    # =====================
    # COST
    # =====================
    ExcelColumn("Budget", lambda x: x.budget, editable=True),
    ExcelColumn("Quantity", lambda x: x.quantity,editable=True),
    ExcelColumn("Unit", lambda x: x.unit,
                column_type=ExcelColumnType.DROPDOWN,
                options=[unit.value for unit in UnitOfMeasure],
                editable=True),

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
