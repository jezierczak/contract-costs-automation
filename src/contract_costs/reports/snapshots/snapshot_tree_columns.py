from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column_v2.tree_options import TreeOptions
from contract_costs.services.snapshots.dto.contract_snapshot_list_dto import ContractSnapshotListDTO


def snapshot_tree_columns()-> list[ExcelColumn[ContractSnapshotListDTO]]:
    return ExcelColumn.from_lists(
        headers=[
            "CODE",
            "BUDGET",
            "PROG",
            "DONE",
            "NET",
            "NON-DEDUCT",
            "SPEND",
            "RESULT",
            "REV",
            "NAME",
        ],
        getters=[
            lambda n: n.code,
            lambda n: n.planned_budget,
            lambda n: n.progress,
            lambda n: n.planned_budget * n.progress,
            lambda n: n.net,
            lambda n: n.non_deductible,
            lambda n: n.net + n.non_deductible,
            lambda n: (n.planned_budget * n.progress) - (n.net + n.non_deductible),
            lambda n: n.revenue,
            lambda n: n.name,
        ],
        types=[
            ExcelColumnType.TREE,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.PERCENT,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
            ExcelColumnType.DISPLAY,
        ],
        tree=TreeOptions(
            id=lambda n: n.node_id,
            parent_id=lambda n: n.parent_id,
            sort_key=lambda n:  n.code
            # is_active=lambda n: n.is_active,
        ),
        agg=True
    )