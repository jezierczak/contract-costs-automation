from dataclasses import dataclass

from contract_costs.infrastructure.excel.excel_column import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.reports.contracts.contract_financials_format import money
from contract_costs.services.company_dashboard.financials.company_financials import CompanyPeriodFinancials


@dataclass(frozen=True)
class CompanyFinancialsRow:
    label: str
    period: CompanyPeriodFinancials


def company_financials_columns() -> list[ExcelColumn[CompanyFinancialsRow]]:
    return ExcelColumn.from_lists(
        headers=[
            "PERIOD",
            "REVENUE NET",
            "REVENUE CF",
            "COST NET",
            "COST NON-TAX",
            "COST CF",
            "FIXED CF",
            "FIXED NET",
            "RESULT NET",
            "RESULT CF",
        ],
        getters=[
            lambda r: r.label,
            lambda r: money(r.period.revenue.net),
            lambda r: money(r.period.revenue.cashflow),
            lambda r: money(r.period.cost.net),
            lambda r: money(r.period.cost.non_tax),
            lambda r: money(r.period.cost.cashflow),
            lambda r: money(r.period.fixed.cashflow),
            lambda r: money(r.period.fixed.net),
            lambda r: money(r.period.result_net),
            lambda r: money(r.period.result_cashflow),
        ],
        types=[ExcelColumnType.DISPLAY] * 10,
        agg=False,
    )
