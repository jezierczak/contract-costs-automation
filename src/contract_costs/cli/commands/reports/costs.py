from contract_costs.cli.context import get_services
from contract_costs.config import REPORTS_DIR
from contract_costs.services.reports.contract_cost_report_runner import (
    ContractCostReportRunner,
)
from contract_costs.services.reports.renders.cli import render_stdout
from contract_costs.services.reports.renders.excel import ExcelReportRenderer
from uuid import UUID


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
    )

    if args.format == "excel":
        path = REPORTS_DIR / f"contract_costs_{contract.code}.xlsx"
        ExcelReportRenderer().render(df, output_path=path)
        print(f"Report saved to {path}")
    else:
        render_stdout(df)
