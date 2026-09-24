from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
# from contract_costs.infrastructure.excel.excel_column_v2.excel_column_type import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column import ExcelColumnType
from contract_costs.reports.contracts.contract_financials_format import level, money
from contract_costs.services.contracts.query.dto.contract_list_dto import ContractListDTO


def contract_list_columns() -> list[ExcelColumn[ContractListDTO]]:
    return ExcelColumn.from_lists(
        headers=[
            "CODE",
            "NAME",
            "STATUS",
            "BUDGET",
            "PROGRESS %",
            "DONE",
            "COST NET",
            "COST NON-TAX",
            "COST CF",
            "REVENUE NET",
            "RESULT ON PROGRESS",
            "FORECAST RESULT",
            "BILLING GAP",
            "COST",
            "SCHEDULE",
            "BILLING",
            "STALE",
        ],
        getters=[
            lambda c: c.code,
            lambda c: c.name,
            lambda c: c.status,
            lambda c: money(c.financials.total.budget),
            lambda c: c.financials.total.progress,
            lambda c: money(c.financials.total.executed),
            lambda c: money(c.financials.total.cost.net),
            lambda c: money(c.financials.total.cost.non_tax),
            lambda c: money(c.financials.total.cost.cashflow),
            lambda c: money(c.financials.total.revenue.net),
            lambda c: money(c.financials.total.result_on_progress),
            lambda c: money(c.financials.total.forecast_result),
            lambda c: money(c.financials.total.billing_gap),
            lambda c: level(c.financials.indicators.cost),
            lambda c: level(c.financials.indicators.schedule),
            lambda c: level(c.financials.indicators.billing),
            lambda c: {True: "yes", False: "no", None: "-"}[c.financials.indicators.progress_stale],
        ],
        types=[
            ExcelColumnType.DISPLAY,  # code
            ExcelColumnType.DISPLAY,  # name
            ExcelColumnType.DISPLAY,  # status
            ExcelColumnType.DISPLAY,  # budget
            ExcelColumnType.PERCENT,  # progress
            ExcelColumnType.DISPLAY,  # done
            ExcelColumnType.DISPLAY,  # cost net
            ExcelColumnType.DISPLAY,  # cost non-tax
            ExcelColumnType.DISPLAY,  # cost cashflow
            ExcelColumnType.DISPLAY,  # revenue net
            ExcelColumnType.DISPLAY,  # result on progress
            ExcelColumnType.DISPLAY,  # forecast result
            ExcelColumnType.DISPLAY,  # billing gap
            ExcelColumnType.DISPLAY,  # cost indicator
            ExcelColumnType.DISPLAY,  # schedule indicator
            ExcelColumnType.DISPLAY,  # billing indicator
            ExcelColumnType.DISPLAY,  # stale
        ],
        agg=[
            False,  # code
            False,  # name
            False,  # status
            True,   # budget
            False,  # progress
            True,   # done
            True,   # cost net
            True,   # cost non-tax
            True,   # cost cashflow
            True,   # revenue net
            True,   # result on progress
            False,  # forecast result
            True,   # billing gap
            False,  # cost indicator
            False,  # schedule indicator
            False,  # billing indicator
            False,  # stale
        ],
    )
