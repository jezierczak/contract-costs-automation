import logging
from uuid import UUID

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY

logger = logging.getLogger(__name__)


def build_show_contracts(subparsers):
    p = subparsers.add_parser(
        "contracts",
        help="Show contracts",
    )

    p.add_argument(
        "ref",
        nargs="?",
        help="Contract UUID or code",
    )

    p.add_argument(
        "--active",
        action="store_true",
        help="Show only active contracts",
    )

    p.set_defaults(handler=handle_show_contracts)


def handle_show_contracts(args) -> None:
    services = get_services()
    repo = services.contract_repository

    # ---------- SINGLE CONTRACT ----------
    if args.ref:
        contract = _resolve_contract(args.ref, repo)

        print("Contract details:")
        print(f"ID:        {contract.id}")
        print(f"Code:      {contract.code}")
        print(f"Name:      {contract.name}")
        print(f"Active:    {contract.is_active}")
        print(f"Start:     {contract.start_date}")
        print(f"End:       {contract.end_date}")
        return

    # ---------- LIST CONTRACTS ----------
    contracts = repo.list()

    if args.active:
        contracts = [c for c in contracts if c.is_active]

    if not contracts:
        print("No contracts found.")
        return

    print(f"{'CODE':<12} {'NAME':<30} {'STATUS'}")
    print("-" * 55)

    for c in contracts:
        print(
            f"{c.code:<12} "
            f"{(c.name or ''):<30} "
            f"{ c.status.value}"
        )


# ---------- utils ----------

def _resolve_contract(ref: str, repo):
    try:
        contract = repo.get(UUID(ref))
        if contract:
            return contract
    except ValueError:
        pass

    contract = repo.get_by_code(ref)
    if contract:
        return contract

    raise RuntimeError(f"Contract not found: {ref}")


REGISTRY.register_group("show", build_show_contracts)
