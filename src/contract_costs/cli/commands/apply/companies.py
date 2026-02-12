from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_user_id, require_organization_id
from contract_costs.common.context.exceptions import ContextError

from contract_costs.infrastructure.excel.excel_loader import ExcelLoader
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InputsCompaniesAssignmentFileManager
from contract_costs.services.companies.apply.adapters.company_excel_action_mapper import CompanyExcelActionMapper
from contract_costs.services.companies.apply.command import ApplyCompaniesCommand
from contract_costs.services.companies.prepare.company_prepare_columns import (
    COMPANY_PREPARE_COLUMNS,
)


def build_apply_companies(subparsers) -> None:
    p = subparsers.add_parser(
        "companies",
        help="Apply companies changes from Excel",
    )
    p.set_defaults(handler=handle_apply_companies)


REGISTRY.register_group("apply", build_apply_companies)

def handle_apply_companies(args) -> None:
    services = get_services()

    try:
        organization_id = require_organization_id(services.context)
        user_id = require_user_id(services.context)
    except ContextError:
        return


    fm = InputsCompaniesAssignmentFileManager(organization_id=organization_id)
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

    apply_command = ApplyCompaniesCommand(
        organization_id=organization_id,
        actor_user_id=user_id,
        commands=commands,
    )

    # =====================
    # APPLY
    # =====================
    services.apply_companies_from_excel_service.execute(apply_command)

    fm.mark_processed()
    print(f"Applied {len(commands)} company commands from {input_path}")
