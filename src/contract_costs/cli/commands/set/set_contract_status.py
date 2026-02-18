from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.cli.utils.contract_resolver import resolve_contract
from contract_costs.common.context.exceptions import ContextError
from contract_costs.cli.context import get_services
from contract_costs.model.contract import ContractStatus
from contract_costs.services.contracts.apply.command.set_contract_status_command import (
    SetContractStatusCommand
)

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



def handle_set_contract_status(args) -> None:
    services = get_services()
    repo = services.contract_repository

    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    contract = resolve_contract(args.ref, organization_id, repo)
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
        organization_id=organization_id,
        actor_user_id=actor_user_id,
        contract_id=contract.id,
        new_status=new_status,
    )

    services.action_bus.execute(action=cmd,handler=services.set_contract_status_service)
    print(
        f"Contract '{contract.code}' status changed "
        f"{contract.status.value} → {new_status.value}"
    )
