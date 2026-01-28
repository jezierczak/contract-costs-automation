from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.services.snapshots.dto.contract_snapshot_list_dto import ContractSnapshotListDTO


def snapshot_list_columns() -> list[ExcelColumn[ContractSnapshotListDTO]]:
    return ExcelColumn.from_lists(
        headers=[
            "SNAPSHOT",
            "DATE",
            "CONTRACT",
            "BUDGET",
            "PROG",
            "DONE",
            "NET",
            "NON-DEDUCT",
            "SPEND",
            "RESULT",
            "REV",
        ],
        getters=[
            lambda s: str(s.snapshot_id)[:8],
            lambda s: s.snapshot_date,
            lambda s: s.contract_code,
            lambda s: s.planned_budget,
            lambda s: s.progress,
            lambda s: (s.planned_budget * s.progress),
            lambda s: s.net_cost,
            lambda s: s.non_deductible,
            lambda s: (s.net_cost + s.non_deductible),
            lambda s: (s.planned_budget * s.progress) - (s.net_cost + s.non_deductible),
            lambda s: s.revenue,
        ],
        types=[
            ExcelColumnType.DISPLAY,  # SNAPSHOT
            ExcelColumnType.DISPLAY,  # DATE
            ExcelColumnType.DISPLAY,  # CONTRACT
            ExcelColumnType.DISPLAY,  # BUDGET
            ExcelColumnType.PERCENT,  # PROG
            ExcelColumnType.DISPLAY,  # DONE
            ExcelColumnType.DISPLAY,  # NET
            ExcelColumnType.DISPLAY,  # NON-DEDUCT
            ExcelColumnType.DISPLAY,  # SPEND
            ExcelColumnType.DISPLAY,  # RESULT
            ExcelColumnType.DISPLAY,  # REV
        ],
        agg=[
            False,  # SNAPSHOT
            False,  # DATE
            False,  # CONTRACT
            True,  # BUDGET
            False,  # PROG
            True,  # DONE
            True,  # NET
            True,  # NON-DEDUCT
            True,  # SPEND
            True,  # RESULT
            True,  # REV
        ],
    )