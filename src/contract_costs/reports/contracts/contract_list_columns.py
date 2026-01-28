from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.services.contracts.query.dto.contract_list_dto import ContractListDTO


def contract_list_columns() -> list[ExcelColumn[ContractListDTO]]:
    return ExcelColumn.from_lists(
        headers=[
            "CODE",
            "NAME",
            "ACTIVE",
            "BUDGET",
            "PROGRESS %",
            "DONE",
            "NET",
            "NON-DEDUCT",
            "SPEND",
            "RESULT",
            "REVENUE",
        ],
        getters=[
            lambda c: c.code,
            lambda c: c.name,
            lambda c: c.is_active,
            lambda c: c.planned_budget,
            lambda c: c.progress if c.progress is not None else None,
            lambda c: (c.planned_budget * c.progress) if c.progress is not None else None,
            lambda c: c.net,
            lambda c: c.non_deduction,
            lambda c: c.net + c.non_deduction,
            lambda c: (
                (c.planned_budget * c.progress) - (c.net + c.non_deduction)
                if c.progress is not None
                else None
            ),
            lambda c: c.revenue,
        ],
        types=[
            ExcelColumnType.DISPLAY,  # code
            ExcelColumnType.DISPLAY,  # name
            ExcelColumnType.CHECKBOX,     # active
            ExcelColumnType.DISPLAY,  # budget
            ExcelColumnType.PERCENT,  # progress
            ExcelColumnType.DISPLAY,  # done
            ExcelColumnType.DISPLAY,  # net
            ExcelColumnType.DISPLAY,  # non-deduct
            ExcelColumnType.DISPLAY,  # spend
            ExcelColumnType.DISPLAY,  # result
            ExcelColumnType.DISPLAY,  # revenue
        ],
        agg=[
            False,  # code
            False,  # name
            False,  # active
            True,   # budget
            False,  # progress
            True,   # done
            True,   # net
            True,   # non-deduct
            True,   # spend
            True,   # result
            True,   # revenue
        ],
    )
