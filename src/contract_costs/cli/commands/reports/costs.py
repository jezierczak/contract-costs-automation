from contract_costs.cli.context import get_services
from contract_costs.config import REPORTS_DIR
from contract_costs.services.reports.contract_cost_report_runner import (
    ContractCostReportRunner,
)
from contract_costs.services.reports.renders.cli import render_stdout
from contract_costs.services.reports.renders.excel import ExcelReportRenderer
from uuid import UUID
from contract_costs.cli.registry import REGISTRY

def build_report_costs(subparsers):
    p = subparsers.add_parser("costs", help="Contract cost report")

    p.add_argument("contract_ref", help="Contract UUID or code",)
    p.add_argument("--group-by", nargs="+", choices=["cost_node", "cost_type", "invoice"], default=["cost_node"],help="Grouping fields (default: cost_node)")
    p.add_argument("--output", choices=["stdout", "excel"], default="stdout",help="Output format")
    p.add_argument("--invoice", nargs="+", help="Filter by invoice numbers")
    p.add_argument("--status", nargs="+",choices=["NEW", "IN_PROGRESS","PROCESSED", "PAID","NOT_PAID", "DELETED"],
        help="Filter by invoice status")

    p.set_defaults(handler=handle_report_costs)


def resolve_contract_ref(repo, ref: str):
    try:
        return repo.get(UUID(ref))
    except (ValueError, TypeError):
        return repo.get_by_code(ref)


def handle_report_costs(args):
    services = get_services()

    contract = resolve_contract_ref(
        services.contract_repository,
        args.contract_ref,
    )

    if contract is None:
        raise ValueError(f"Contract '{args.contract_ref}' not found")

    runner = ContractCostReportRunner(
        services.contract_cost_report
    )

    df = runner.run(
        contract_id=contract.id,
        group_by=args.group_by,
        invoice_numbers=args.invoice,
        invoice_statuses=args.status,
    )

    if args.output == "excel":
        path = REPORTS_DIR / f"contract_costs_{contract.code}.xlsx"
        ExcelReportRenderer().render(df, output_path=path)
        print(f"Report saved to {path}")
    else:
        render_stdout(df)

REGISTRY.register_group("report", build_report_costs)
