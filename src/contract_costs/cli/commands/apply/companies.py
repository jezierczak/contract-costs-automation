from pathlib import Path

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.infrastructure.excel.excel_loader import ExcelLoader
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InputsCompaniesAssignmentFileManager
from contract_costs.services.companies.apply.adapters.company_excel_action_mapper import CompanyExcelActionMapper
from contract_costs.services.companies.prepare.company_prepare_columns import (
    COMPANY_PREPARE_COLUMNS,
)

import contract_costs.config as cfg


def build_apply_companies(subparsers) -> None:
    p = subparsers.add_parser(
        "companies",
        help="Apply companies changes from Excel",
    )

    # p.add_argument(
    #     "--input",
    #     help="Input Excel file path",
    # )

    p.set_defaults(handler=handle_apply_companies)


REGISTRY.register_group("apply", build_apply_companies)

def handle_apply_companies(args) -> None:
    services = get_services()

    # if args.input:
    #     input_path = Path(args.input)
    # else:
    #     input_path = cfg.INPUTS_COMPANIES_EDIT_DIR / "companies.xlsx"

    # if not input_path.exists():
    #     print(f"Input file not found: {input_path}")
    #     return
    fm = InputsCompaniesAssignmentFileManager()
    input_path = fm.get_active_file()
    # =====================
    # LOAD EXCEL → ROWS
    # =====================
    rows = ExcelLoader.load(
        input_path=input_path,
        columns=COMPANY_PREPARE_COLUMNS,
        sheet_name="companies",
    )

    if not rows:
        print("No rows found in Excel.")
        return

    # =====================
    # MAP → COMMANDS
    # =====================
    commands = [
        CompanyExcelActionMapper.map(row)
        for row in rows
    ]

    # =====================
    # APPLY
    # =====================
    services.apply_companies_from_excel_service.apply(commands)
    fm.mark_processed()
    print(f"Applied {len(commands)} company commands from {input_path}")
