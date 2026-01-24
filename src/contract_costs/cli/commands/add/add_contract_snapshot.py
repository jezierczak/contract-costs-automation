from datetime import date

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.contract_resolver import resolve_contract


def build_add_contract_snapshot(subparsers):
    p = subparsers.add_parser(
        "contract-snapshot",
        aliases=["snapshot"],
        help="Create contract snapshot",
    )
    p.add_argument("ref", help="Contract UUID or code")
    p.add_argument(
        "--date",
        help="Snapshot date (YYYY-MM-DD), default=today",
    )
    p.set_defaults(handler=handle_add_contract_snapshot)

REGISTRY.register_group("add", build_add_contract_snapshot)

def handle_add_contract_snapshot(args):
    services = get_services()
    contract = resolve_contract(args.ref, services)

    snapshot_date = (
        date.fromisoformat(args.date)
        if args.date
        else date.today()
    )

    snapshot,created = services.create_contract_snapshot.create(
        contract_id=contract.id,
        snapshot_date=snapshot_date,
    )

    if created:
        print(
            f"Snapshot created: "
            f"contract={contract.code} "
            f"date={snapshot.snapshot_date}"
        )
    else:
        print(f"Snapshot already exists: contract={contract.code} date={snapshot.snapshot_date}")