import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.contract_resolver import resolve_contract
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InputsContractsProgressFileManager

logger = logging.getLogger(__name__)


# =========================================================
# BUILDER (argparse)
# =========================================================

def build_prepare_contract_progress(subparsers):
    p = subparsers.add_parser(
        "contract-progress",
        help="Prepare contract progress editing file (Excel)",
    )
    p.add_argument(
        "ref",
        help="Contract reference: UUID or code",
    )


    p.set_defaults(handler=handle_prepare_contract_progress)

REGISTRY.register_group("prepare", build_prepare_contract_progress)
# =========================================================
# HANDLER
# =========================================================

def handle_prepare_contract_progress(args) -> None:
    contract_ref = args.ref
    services = get_services()

    contract = resolve_contract(contract_ref, services)

    fm = InputsContractsProgressFileManager(contract_code=contract.code)
    output_path = fm.prepare_target()

    exporter = services.contract_prepare_progress_excel_exporter

    exporter.export_existing(
        contract=contract,
        cost_nodes=services.contract_node_repository.list_by_contract(contract.id),
        output_path=output_path,
    )

    logger.info(
        "Contract progress Excel generated: contract=%s path=%s",
        contract.code,
        output_path,
    )
    print(
        f"Prepared contract progress for '{contract.code}':\n{output_path}"
    )
