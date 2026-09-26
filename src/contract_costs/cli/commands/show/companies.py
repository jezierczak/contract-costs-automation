from contract_costs.cli.context import get_services
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.printers.table_printer.table_printer import TablePrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.common.context.exceptions import ContextError
from contract_costs.model.company import CompanyType
from contract_costs.reports.companies.company_list_columns import company_list_columns
from contract_costs.services.companies.query.dto.company_dto import CompanyDTO
from contract_costs.services.companies.query.dto.company_query import CompanyQuery


def build_show_companies(subparsers):
    p = subparsers.add_parser(
        "companies",
        help="Show companies",
    )

    p.add_argument("--own", action="store_true", help="Show own companies only")
    p.add_argument("--inactive", action="store_true", help="Include inactive companies")
    p.add_argument("--to-verify", action="store_true", help="Show companies waiting for verification only")
    p.add_argument("--nip", help="Filter by tax number (strict)")
    p.add_argument("--search", help="Search in name, description, address, email")
    p.add_argument("--role", help="Filter by company role")

    p.set_defaults(handler=handle_show_companies)

REGISTRY.register_group("show", build_show_companies)


def handle_show_companies(args) -> None:
    services = get_services()
    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    role = None
    if args.role:
        try:
            role = CompanyType[args.role.upper()]
        except KeyError:
            print(f"Invalid role: {args.role}")
            return

    query = CompanyQuery(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        tax_number=args.nip,
        own_only=args.own,
        include_inactive=args.inactive,
        to_verify_only=args.to_verify,
        search=args.search,
        role=role,
    )

    items = services.action_bus.execute(action=query,handler=services.company_query_service)
    if not items:
        print("No companies found.")
        return

    columns = company_list_columns()

    header = {
        "Report": ["Companies list"],
        "Count": [str(len(items))],
    }

    printer: TablePrinter[CompanyDTO] = CmdPrinter(style="pipe")
    printer.print(
        organization_id=str(organization_id),
        items=items,
        columns=columns,
        header=header,
    )


# def handle_show_companies(args) -> None:
#     services = get_services()
#
#     role = None
#     if args.role:
#         try:
#             role = CompanyType[args.role.upper()]
#         except KeyError:
#             print(f"Invalid role: {args.role}")
#             return
#
#     query = CompanyQuery(
#         tax_number=args.nip,
#         own_only=args.own,
#         include_inactive=args.inactive,
#         search=args.search,
#         role=role,
#     )
#
#     companies = services.company_query_service.list_companies(query)
#
#     if not companies:
#         print("No companies found.")
#         return
#
#     CompanyTablePrinter.print(companies)


