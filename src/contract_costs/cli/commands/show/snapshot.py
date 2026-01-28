from datetime import datetime

from contract_costs.cli.context import get_services
from contract_costs.cli.printers.table_printer.cmd_printer import CmdPrinter
from contract_costs.cli.printers.table_printer.excel_printer import ExcelPrinter
from contract_costs.cli.registry import REGISTRY
from contract_costs.infrastructure.filesystem.show_file_manager import  SnapshotShowFileManager
from contract_costs.reports.snapshots.snapshot_tree_columns import snapshot_tree_columns


# =========================================================
# BUILDER
# =========================================================

def build_show_snapshot(subparsers):
    p = subparsers.add_parser(
        "snapshot",
        help="Show contract snapshot details",
    )

    p.add_argument(
        "snapshot_id",
        nargs="?",
        help="Snapshot UUID",
    )

    p.add_argument(
        "--excel",
        action="store_true",
        help="Export snapshot to Excel",
    )

    p.set_defaults(handler=handle_show_snapshot)


REGISTRY.register_group("show", build_show_snapshot)

def handle_show_snapshot(args):
    services = get_services()
    query = services.contract_snapshot_query_service

    snapshot_ref = args.snapshot_id

    dto = query.get_snapshot(snapshot_id=snapshot_ref)

    header = {
        "Snapshot ID": [str(dto.snapshot_id)],
        "Snapshot Date": [str(dto.snapshot_date)],
        "Contract": [dto.contract_code],
        "Generated": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    }


    if args.excel:

        fm = SnapshotShowFileManager(
            contract_code=dto.contract_code,
            contract_date=dto.snapshot_date,
        )
        output_path = fm.create_output_file()

        printer = ExcelPrinter(output_path)
        printer.print(
            items=dto.nodes,
            columns=snapshot_tree_columns(),
            header=header,
        )
        print(f"Contract snapshot exported to Excel: {output_path}")
        return

    printer = CmdPrinter()
    printer.print(
        items=dto.nodes,
        columns=snapshot_tree_columns(),
        header=header,
    )

