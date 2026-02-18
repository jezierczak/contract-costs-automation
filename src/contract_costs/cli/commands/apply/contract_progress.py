from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.cli.utils.contract_resolver import resolve_contract
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InputsContractsProgressFileManager
from contract_costs.services.contracts.apply.command.apply_contract_progress_excel_command import \
    ApplyContractProgressExcelCommand


def build_apply_contract_progress(subparsers):
    p = subparsers.add_parser(
        "contract-progress",
        help="Apply contract progress from Excel",
    )

    p.add_argument(
        "ref",
        help="Contract reference: UUID or code",
    )

    p.set_defaults(handler=handle_apply_contract_progress)

REGISTRY.register_group("apply", build_apply_contract_progress)

def handle_apply_contract_progress(args) -> None:
    services = get_services()
    ref = args.ref
    try:
        organization_id = require_organization_id(services.context)
        actor_user_id = require_user_id(services.context)
    except ContextError:
        return

    contract = resolve_contract(ref,organization_id, services)

    fm = InputsContractsProgressFileManager(
        organization_id=organization_id,
        contract_code=contract.code)
    excel_path = fm.get_active_file()

    services.action_bus.execute(
        action=ApplyContractProgressExcelCommand(
            contract_id=contract.id,
            excel_path=excel_path,
            organization_id=organization_id,
            actor_user_id=actor_user_id
        ),
        handler=services.apply_contract_progress_excel
    )

    fm.mark_processed()

    print(f"Contract progress applied for '{contract.code}'.")
