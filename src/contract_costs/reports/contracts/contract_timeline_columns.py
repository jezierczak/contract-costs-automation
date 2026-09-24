from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.infrastructure.excel.excel_column import ExcelColumnType
from contract_costs.reports.contracts.contract_financials_format import money
from contract_costs.services.contracts.financials.contract_timeline import ContractMonth


def contract_timeline_columns() -> list[ExcelColumn[ContractMonth]]:
    return ExcelColumn.from_lists(
        headers=[
            "MONTH",
            "COST NET",
            "COST NON-TAX",
            "COST CF",
            "REVENUE NET",
            "REVENUE CF",
            "CUM COST CF",
            "CUM REVENUE CF",
            "CUM DONE",
            "CUM RESULT ON PROGRESS",
        ],
        getters=[
            lambda m: f"{m.year}-{m.month:02d}",
            lambda m: money(m.cost.net),
            lambda m: money(m.cost.non_tax),
            lambda m: money(m.cost.cashflow),
            lambda m: money(m.revenue.net),
            lambda m: money(m.revenue.cashflow),
            lambda m: money(m.cumulative_cost.cashflow),
            lambda m: money(m.cumulative_revenue.cashflow),
            lambda m: money(m.executed_cumulative),
            lambda m: money(m.result_on_progress_cumulative),
        ],
        types=[ExcelColumnType.DISPLAY] * 10,
        agg=[False, True, True, True, True, True, False, False, False, False],
    )
