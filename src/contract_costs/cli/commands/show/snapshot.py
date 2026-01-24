from uuid import UUID

from contract_costs.cli.context import get_services
from contract_costs.cli.printers.snapshot_tree_printer import print_snapshot_tree
from contract_costs.cli.registry import REGISTRY


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

    p.set_defaults(handler=handle_show_snapshot)


REGISTRY.register_group("show", build_show_snapshot)

def handle_show_snapshot(args):
    services = get_services()
    query = services.contract_snapshot_query_service

    snapshot_id = args.snapshot_id
    dto = query.get_snapshot(snapshot_id=snapshot_id)
    print_snapshot_tree(dto.nodes)
