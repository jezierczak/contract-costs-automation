from datetime import datetime

from contract_costs.cli.context import get_services
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.printers.table_printer.excel_printer import ExcelPrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id
from contract_costs.cli.utils.contract_resolver import resolve_contract
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.show_file_manager import SnapshotsShowFileManager
from contract_costs.reports.snapshots.snapshot_list_columns import snapshot_list_columns



# =========================================================
# BUILDER
# =========================================================

def build_show_snapshots(subparsers):
    p = subparsers.add_parser(
        "snapshots",
        help="Show contract snapshots",
    )

    p.add_argument(
        "ref",
        nargs="?",
        help="Contract UUID or code (optional)",
    )

    p.add_argument(
        "--excel",
        action="store_true",
        help="Export snapshot to Excel",
    )

    p.set_defaults(handler=handle_show_snapshots)


REGISTRY.register_group("show", build_show_snapshots)

# =========================================================
# HANDLER
# =========================================================

def handle_show_snapshots(args):
    services = get_services()
    query = services.contract_snapshot_query_service

    try:
        organization_id = require_organization_id(services.context)
    except ContextError:
        return

    if args.ref:
        contract = resolve_contract(args.ref, organization_id, services)

        rows = query.list_snapshots(
            organization_id=organization_id,
            contract_id=contract.id,
        )
        contract_code = contract.code
    else:
        rows = query.list_snapshots(
            organization_id=organization_id,
        )
        contract_code = None

    columns = snapshot_list_columns()

    header = {
        "Contract": [contract_code] if contract_code else ["ALL"],
        "Generated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    }

    if args.excel:
        fm = SnapshotsShowFileManager(
            organization_id=organization_id,
            contract_code=contract_code)
        output_path = fm.create_output_file()

        printer = ExcelPrinter(output_path=output_path)
        printer.print(
            items=rows,
            columns=columns,
            header=header,
        )
        print(f"Contract snapshots exported to Excel: {output_path}")
        return

    printer = CmdPrinter()
    printer.print(
        items=rows,
        columns=columns,
        header=header,
    )
