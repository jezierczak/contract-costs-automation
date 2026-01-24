from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.contract_resolver import resolve_contract
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InputsContractsProgressFileManager


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

    contract = resolve_contract(ref, services)

    fm = InputsContractsProgressFileManager(contract_code=contract.code)
    excel_path = fm.get_active_file()

    services.apply_contract_progress_excel.apply(
        contract=contract,
        excel_path=excel_path,
    )

    fm.mark_processed()

    print(f"Contract progress applied for '{contract.code}'.")
