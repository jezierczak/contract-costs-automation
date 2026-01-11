from pathlib import Path

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.infrastructure.excel.base_excel_exporter import BaseExcelExporter
from contract_costs.model.company import CompanyType
from contract_costs.services.companies.query.company_query_service import CompanyQuery
from contract_costs.services.companies.prepare.company_prepare_columns import (
    COMPANY_PREPARE_COLUMNS,
)
import contract_costs.config as cfg


# =====================
# CLI REGISTRATION
# =====================
def build_prepare_companies(subparsers) -> None:
    p = subparsers.add_parser(
        "companies",
        help="Prepare companies Excel for editing",
    )

    p.add_argument(
        "--output",
        help="Output Excel file path",
    )

    p.add_argument(
        "--nip",
        help="Filter by tax number (strict)",
    )
    p.add_argument("--inactive", action="store_true", help="Include inactive companies")
    p.add_argument("--own", action="store_true", help="Show own companies only")
    p.add_argument("--search", help="Search in name, description, address, email")
    p.add_argument("--role", help="Filter by company role")

    p.set_defaults(handler=handle_prepare_companies)


REGISTRY.register_group("prepare", build_prepare_companies)


def handle_prepare_companies(args) -> None:
    services = get_services()

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = cfg.INPUTS_COMPANIES_EDIT_DIR / "companies.xlsx"

    role = None
    if args.role:
        try:
            role = CompanyType[args.role.upper()]
        except KeyError:
            print(f"Invalid role: {args.role}")
            return
    # =====================
    # QUERY (READ ONLY)
    # =====================
    query = CompanyQuery(
        tax_number=args.nip,
        own_only=args.own,
        include_inactive=args.inactive,
        search=args.search,
        role=role,
    )

    companies = services.company_query_service.list_companies(query)

    if not companies:
        print("No companies found to prepare.")
        return

    # =====================
    # EXPORT TO EXCEL
    # =====================
    BaseExcelExporter.export(
        items=companies,
        columns=COMPANY_PREPARE_COLUMNS,
        output_path=output_path,
        sheet_name="companies",
    )

    print(f"Prepared {len(companies)} companies → {output_path}")

