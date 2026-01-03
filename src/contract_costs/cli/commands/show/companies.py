from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.model.company import CompanyType


def build_show_companies(subparsers):
    p = subparsers.add_parser(
        "companies",
        help="Show companies",
    )

    p.add_argument("--own", action="store_true")
    p.add_argument("--inactive", action="store_true")

    p.set_defaults(handler=handle_show_companies)


def handle_show_companies(args):
    services = get_services()
    repo = services.company_repository

    companies = repo.list_all()

    if args.own:
        companies = [c for c in companies if c.role == CompanyType.OWN]

    if not args.inactive:
        companies = [c for c in companies if c.is_active]

    if not companies:
        print("No companies found.")
        return

    for c in companies:
        print(
            f"{c.id} | {c.name} | {c.tax_number} | {c.role.value} | active={c.is_active}"
        )


REGISTRY.register_group("show", build_show_companies)
