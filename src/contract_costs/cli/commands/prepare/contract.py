import logging

from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.cli.utils.context_helpers import require_organization_id, require_user_id
from contract_costs.cli.utils.contract_resolver import resolve_contract
from contract_costs.common.context.exceptions import ContextError
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InputsContractsAssignmentFileManager

logger = logging.getLogger(__name__)


# =========================================================
# BUILDER (argparse)
# =========================================================

def build_prepare_contract(subparsers):
    p = subparsers.add_parser(
        "contract",
        help="Prepare contract structure for editing (Excel)",
    )

    p.add_argument(
        "ref",
        help="Contract reference: 'new' or UUID/code",
    )

    p.set_defaults(handler=handle_prepare_contract)

REGISTRY.register_group("prepare", build_prepare_contract)

# =========================================================
# HANDLER
# =========================================================

def handle_prepare_contract(args) -> None:
    """
    prepare contract new
    prepare contract <UUID|CODE>
    """
    contract_ref = args.ref
    services = get_services()

    exporter = services.contract_prepare_excel_exporter

    try:
        organization_id = require_organization_id(services.context)
        # actor_user_id = require_user_id(services.context)
    except ContextError:
        return


    if contract_ref == "new":
        fm = InputsContractsAssignmentFileManager(organization_id=organization_id)

        output_path = fm.prepare_target()
        exporter.export_new(output_path=output_path,organization_id=organization_id)
        logger.info("Empty contract structure Excel generated: %s", output_path)
        print(f"Prepared NEW contract Excel:\n{output_path}")
        return
    else:
        contract = resolve_contract(contract_ref,organization_id, services)

        fm = InputsContractsAssignmentFileManager(
            organization_id=organization_id,
            contract_code=contract.code)

        output_path = fm.prepare_target()

        # TODO zamienić to na query !!
        exporter.export_existing(
            organization_id=organization_id,
            contract=contract,
            cost_nodes=services.contract_node_repository.list_by_contract(
                organization_id=organization_id,
                contract_id=contract.id
            ),
            output_path=output_path
        )

        logger.info(
            "Contract structure Excel generated: contract=%s path=%s",
            contract.code,
            output_path,
        )
        print(f"Prepared contract '{contract.code}' for editing:\n{output_path}")



