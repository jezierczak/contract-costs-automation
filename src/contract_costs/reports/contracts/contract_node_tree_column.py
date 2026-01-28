from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column_v2.tree_options import TreeOptions
from contract_costs.services.contracts.query.dto.contract_node_details_dto import ContractNodeDetailsDTO


def contract_node_tree_columns() -> list[ExcelColumn[ContractNodeDetailsDTO]]:
    return ExcelColumn.from_lists(
        headers=[
            "CODE",
            "NAME",
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
            lambda n: f"[{n.code}]" if not n.is_leaf else n.code,
            lambda n: n.name,
            lambda n: n.planned_budget,
            lambda n: n.progress if n.progress is not None else None,
            lambda n: (
                n.planned_budget * n.progress
                if n.progress is not None
                else None
            ),
            lambda n: n.net,
            lambda n: n.non_deductible,
            lambda n: n.net + n.non_deductible,
            lambda n: (
                (n.planned_budget * n.progress) - (n.net + n.non_deductible)
                if n.progress is not None
                else None
            ),
            lambda n: n.revenue,
        ],
        types=[
            ExcelColumnType.TREE,     # code
            ExcelColumnType.DISPLAY,  # name
            ExcelColumnType.DISPLAY,  # budget
            ExcelColumnType.PERCENT,  # progress
            ExcelColumnType.DISPLAY,  # done
            ExcelColumnType.DISPLAY,  # net
            ExcelColumnType.DISPLAY,  # non-deduct
            ExcelColumnType.DISPLAY,  # spend
            ExcelColumnType.DISPLAY,  # result
            ExcelColumnType.DISPLAY,  # revenue
        ],
        tree=TreeOptions(
            id=lambda n: n.node_id,
            parent_id=lambda n: n.parent_id,
            sort_key=lambda n: n.code
            # is_active=lambda n: n.is_active,
        ),
        # agg=[False] * 10,  # brak sumowania na dole
    )
