from contract_costs.cli.registry import REGISTRY

def build_set_contract_status(subparsers):
    p = subparsers.add_parser(
        "contract-status",
        help="Set contract status",
    )

    p.add_argument(
        "ref",
        help="Contract UUID or code",
    )

    p.add_argument(
        "status",
        help="New status (planned, active, finished, cancelled)",
    )

    p.set_defaults(handler=handle_set_contract_status)

REGISTRY.register_group("set", build_set_contract_status)

from uuid import UUID

from contract_costs.cli.context import get_services
from contract_costs.model.contract import ContractStatus
from contract_costs.services.contracts.apply.command.set_contract_status_command import (
    SetContractStatusCommand
)

def handle_set_contract_status(args) -> None:
    services = get_services()
    repo = services.contract_repository

    contract = _resolve_contract(args.ref, repo)
    if not contract:
        print(f"Contract not found: {args.ref}")
        return

    try:
        new_status = ContractStatus[args.status.upper()]
    except KeyError:
        print(f"Invalid status: {args.status}")
        print("Allowed:", ", ".join(s.name.lower() for s in ContractStatus))
        return

    cmd = SetContractStatusCommand(
        contract_id=contract.id,
        new_status=new_status,
    )

    services.set_contract_status_service.execute(cmd)

    print(
        f"Contract '{contract.code}' status changed "
        f"{contract.status.value} → {new_status.value}"
    )


def _resolve_contract(ref: str, repo):
    try:
        return repo.get(UUID(ref))
    except ValueError:
        return repo.get_by_code(ref)
