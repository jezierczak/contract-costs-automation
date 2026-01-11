from contract_costs.cli.context import get_services
from contract_costs.cli.printers.company_printer import CompanyTablePrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.model.company import CompanyType
from contract_costs.services.companies.query.dto.company_query import CompanyQuery


def build_show_companies(subparsers):
    p = subparsers.add_parser(
        "companies",
        help="Show companies",
    )

    p.add_argument("--own", action="store_true", help="Show own companies only")
    p.add_argument("--inactive", action="store_true", help="Include inactive companies")
    p.add_argument("--nip", help="Filter by tax number (strict)")
    p.add_argument("--search", help="Search in name, description, address, email")
    p.add_argument("--role", help="Filter by company role")

    p.set_defaults(handler=handle_show_companies)

REGISTRY.register_group("show", build_show_companies)

def handle_show_companies(args) -> None:
    services = get_services()

    role = None
    if args.role:
        try:
            role = CompanyType[args.role.upper()]
        except KeyError:
            print(f"Invalid role: {args.role}")
            return

    query = CompanyQuery(
        tax_number=args.nip,
        own_only=args.own,
        include_inactive=args.inactive,
        search=args.search,
        role=role,
    )

    companies = services.company_query_service.list_companies(query)

    if not companies:
        print("No companies found.")
        return

    CompanyTablePrinter.print(companies)


