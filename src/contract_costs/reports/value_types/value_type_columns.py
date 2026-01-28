from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.model.value_type import ValueType


def value_type_list_columns() -> list[ExcelColumn[ValueType]]:
    return ExcelColumn.from_lists(
        headers=[
            "CODE",
            "NAME",
            "DESCRIPTION",
            "DIRECTION",
            "ACTIVE",
        ],
        getters=[
            lambda v: v.code,
            lambda v: v.name,
            lambda v: v.description,
            lambda v: v.direction,
            lambda v: v.is_active,
        ],
        types=[
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.CHECKBOX,
        ],
        agg=[
            False,
            False,
            False,
            False,
            False,
        ],
    )
