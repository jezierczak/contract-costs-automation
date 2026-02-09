from datetime import date

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.cli.utils.contract_resolver import resolve_contract
from contract_costs.common.context.exceptions import ContextError
from contract_costs.services.snapshots.dto.create_contract_snapshot_command import CreateContractSnapshotCommand


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

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    contract = resolve_contract(args.ref, organization_id, services)

    snapshot_date = (
        date.fromisoformat(args.date)
        if args.date
        else date.today()
    )

    cmd = CreateContractSnapshotCommand(
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        contract_id=contract.id,
        snapshot_date=snapshot_date,
    )

    snapshot, created = services.create_contract_snapshot.execute(cmd)

    if created:
        print(
            f"Snapshot created: "
            f"contract={contract.code} "
            f"date={snapshot.snapshot_date}"
        )
    else:
        print(
            f"Snapshot already exists: "
            f"contract={contract.code} "
            f"date={snapshot.snapshot_date}"
        )