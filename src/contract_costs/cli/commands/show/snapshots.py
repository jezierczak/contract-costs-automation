from contract_costs.cli.context import get_services
from contract_costs.cli.printers.snapshot_list_printer import print_snapshot_list
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.contract_resolver import resolve_contract


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

    p.set_defaults(handler=handle_show_snapshots)


REGISTRY.register_group("show", build_show_snapshots)

# =========================================================
# HANDLER
# =========================================================

def handle_show_snapshots(args):
    services = get_services()
    query = services.contract_snapshot_query_service

    if args.ref:
        contract = resolve_contract(args.ref, services)
        rows = query.list_snapshots(contract.id)
    else:
        rows = query.list_snapshots()

    print_snapshot_list(rows)
