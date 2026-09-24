from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
# from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column_v2.tree_options import TreeOptions
from contract_costs.reports.contracts.contract_financials_format import money
from contract_costs.services.contracts.query.dto.contract_node_details_dto import ContractNodeDetailsDTO


def contract_node_tree_columns() -> list[ExcelColumn[ContractNodeDetailsDTO]]:
    return ExcelColumn.from_lists(
        headers=[
            "CODE",
            "NAME",
            "BUDGET",
            "PROGRESS %",
            "DONE",
            "COST NET",
            "COST NON-TAX",
            "COST CF",
            "REVENUE NET",
            "RESULT ON PROGRESS",
        ],
        getters=[
            lambda n: f"[{n.code}]" if not n.is_leaf else n.code,
            lambda n: n.name,
            lambda n: money(n.financials.budget),
            lambda n: n.financials.progress,
            lambda n: money(n.financials.executed),
            lambda n: money(n.financials.cost.net),
            lambda n: money(n.financials.cost.non_tax),
            lambda n: money(n.financials.cost.cashflow),
            lambda n: money(n.financials.revenue.net),
            lambda n: money(n.financials.result_on_progress),
        ],
        types=[
            ExcelColumnType.TREE,     # code
            ExcelColumnType.DISPLAY,  # name
            ExcelColumnType.DISPLAY,  # budget
            ExcelColumnType.PERCENT,  # progress
            ExcelColumnType.DISPLAY,  # done
            ExcelColumnType.DISPLAY,  # cost net
            ExcelColumnType.DISPLAY,  # cost non-tax
            ExcelColumnType.DISPLAY,  # cost cashflow
            ExcelColumnType.DISPLAY,  # revenue net
            ExcelColumnType.DISPLAY,  # result on progress
        ],
        tree=TreeOptions(
            id=lambda n: n.node_id,
            parent_id=lambda n: n.parent_id,
            sort_key=lambda n: n.code
            # is_active=lambda n: n.is_active,
        ),
        # agg=[False] * 10,  # brak sumowania na dole
    )
