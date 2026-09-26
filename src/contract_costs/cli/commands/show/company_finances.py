from datetime import datetime
from uuid import UUID

from contract_costs.cli.context import get_services
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.reports.companies.company_financials_columns import (
    CompanyFinancialsRow,
    company_financials_columns,
)
from contract_costs.services.company_dashboard.dto.company_dashboard_query import CompanyDashboardQuery


def build_show_company_finances(subparsers):
    p = subparsers.add_parser(
        "company-finances",
        help="Show own company finances by month (three pillars from Amount)",
    )

    p.add_argument(
        "ref",
        nargs="?",
        help="Own company UUID or tax number (default: first own company)",
    )

    p.add_argument(
        "--year",
        type=int,
        help="Year (default: current year)",
    )

    p.set_defaults(handler=handle_show_company_finances)

REGISTRY.register_group("show", build_show_company_finances)


def handle_show_company_finances(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return None

    company_id, tax_number = _parse_ref(args.ref)

    dashboard = services.action_bus.execute(
        action=CompanyDashboardQuery(
            organization_id=organization_id,
            actor_user_id=actor_user_id,
            company_id=company_id,
            tax_number=tax_number,
            year=args.year,
        ),
        handler=services.company_dashboard_query_service,
    )

    financials = dashboard.financials
    company = next(
        (c for c in dashboard.owner_companies if c.id == dashboard.selected_company_id),
        None,
    )

    rows = [
        CompanyFinancialsRow(label=f"{financials.year}-{month:02d}", period=period)
        for month, period in sorted(financials.months.items())
    ]
    rows.append(CompanyFinancialsRow(label=f"{financials.year} TOTAL", period=financials.total))

    CmdPrinter().print(
        organization_id=str(organization_id),
        items=rows,
        columns=company_financials_columns(),
        header={
            "Report": ["Own company finances"],
            "Company": [company.name if company else str(dashboard.selected_company_id)],
            "Year": [str(financials.year)],
            "Generated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        },
    )

    return None


def _parse_ref(ref: str | None) -> tuple[UUID | None, str | None]:
    if not ref:
        return None, None
    try:
        return UUID(ref), None
    except ValueError:
        return None, ref
