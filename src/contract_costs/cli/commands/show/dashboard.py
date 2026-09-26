from dataclasses import dataclass
from datetime import datetime

from contract_costs.cli.context import get_services
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.excel.excel_column import ExcelColumnType
from contract_costs.infrastructure.excel.excel_column_v2.excel_column import ExcelColumn
from contract_costs.reports.companies.company_financials_columns import (
    CompanyFinancialsRow,
    company_financials_columns,
)
from contract_costs.reports.contracts.contract_financials_format import money
from contract_costs.services.dashboard.dto.dashboard_data import UnpaidSummary
from contract_costs.services.dashboard.dto.dashboard_query import DashboardQuery


@dataclass(frozen=True)
class _UnpaidRow:
    label: str
    summary: UnpaidSummary
    link: str


def build_show_dashboard(subparsers):
    p = subparsers.add_parser(
        "dashboard",
        help="Show organization dashboard: own companies, group result without INTERNAL, unpaid invoices",
    )
    p.set_defaults(handler=handle_show_dashboard)

REGISTRY.register_group("show", build_show_dashboard)


def handle_show_dashboard(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return None

    data = services.action_bus.execute(
        action=DashboardQuery(organization_id=organization_id, actor_user_id=actor_user_id),
        handler=services.dashboard_query_service,
    )

    last_month = f"{data.last_month_year}-{data.last_month:02d}"
    rows: list[CompanyFinancialsRow] = []
    for card in data.companies:
        rows.append(CompanyFinancialsRow(label=f"{card.name} | {data.year}", period=card.periods.year))
        rows.append(CompanyFinancialsRow(label=f"{card.name} | {last_month}", period=card.periods.last_month))
    rows.append(CompanyFinancialsRow(label=f"GRUPA (bez INTERNAL) | {data.year}", period=data.group.year))
    rows.append(CompanyFinancialsRow(label=f"GRUPA (bez INTERNAL) | {last_month}", period=data.group.last_month))

    printer = CmdPrinter()
    printer.print(
        organization_id=str(organization_id),
        items=rows,
        columns=company_financials_columns(),
        header={
            "Report": ["Dashboard"],
            "To assign": [
                f"dokumenty: {data.documents_to_assign} (/documents?status=READY), "
                f"rekordy: {data.records_to_assign} (/records/assign)"
            ],
            "Unapproved": [
                ", ".join(f"{c.name}: {c.unapproved_record_count}" for c in data.companies) or "-"
            ],
            "Generated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        },
    )

    printer.print(
        organization_id=str(organization_id),
        items=[
            _UnpaidRow("Koszty do zapłaty", data.unpaid_costs, "/records/unpaid_costs"),
            _UnpaidRow("Przychody niezapłacone", data.unpaid_revenue, "/records/unpaid_revenue"),
            _UnpaidRow("Wewnętrzne niezapłacone", data.unpaid_internal, "/records/unpaid_internal"),
        ],
        columns=ExcelColumn.from_lists(
            headers=["UNPAID", "COUNT", "GROSS LEFT", "LINK"],
            getters=[
                lambda r: r.label,
                lambda r: str(r.summary.count),
                lambda r: money(r.summary.amount),
                lambda r: r.link,
            ],
            types=[ExcelColumnType.DISPLAY] * 4,
            agg=False,
        ),
    )

    return None
