from uuid import UUID

from contract_costs.cli.context import get_services
from contract_costs.cli.printers.snapshot_tree_printer import print_snapshot_tree
from contract_costs.cli.registry import REGISTRY
from contract_costs.infrastructure.excel.contracts.contract_snapshot_excel_exporter import ContractSnapshotExcelExporter
from contract_costs.infrastructure.filesystem.show_file_manager import ContractsShowFileManager, \
    SnapshotsShowFileManager


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

    if args.excel:
        exporter = ContractSnapshotExcelExporter()

        fm = SnapshotsShowFileManager(
            contract_code=dto.contract_code,
            contract_date=dto.snapshot_date,
        )
        output_path = fm.create_output_file()

        exporter.export(
            snapshot=dto,
            output_path=output_path,
        )
        print(f"Contract snapshot exported to Excel: {output_path}")
        return

    print(f"\nSNAPSHOT {dto.snapshot_id} | {dto.contract_code} | {dto.snapshot_date}\n")
    print_snapshot_tree(dto.nodes)

