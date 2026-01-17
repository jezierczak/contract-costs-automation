import logging
from uuid import UUID

import contract_costs.config as cfg
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY
from contract_costs.infrastructure.filesystem.excel_domain_file_manager import InputsContractsAssignmentFileManager

logger = logging.getLogger(__name__)


# =========================================================
# BUILDER
# =========================================================

def build_apply_contract(subparsers):
    p = subparsers.add_parser(
        "contract",
        help="Apply contract changes from Excel",
    )

    p.add_argument(
        "ref",
        help="Contract reference: 'new' or UUID/code",
    )

    p.set_defaults(handler=handle_apply_contract)


# =========================================================
# HANDLER
# =========================================================

def handle_apply_contract(args) -> None:
    services = get_services()
    ref = args.ref

    if ref == "new":
        fm = InputsContractsAssignmentFileManager()
        excel_path = fm.get_active_file()

        services.apply_contract_structure_excel.apply_new(excel_path)

        fm.mark_processed()  # 🔒 DOMKNIĘCIE LIFECYCLE

        print("New contract applied from Excel.")
        return

    contract = _resolve_contract(ref, services)

    fm = InputsContractsAssignmentFileManager(contract_code=contract.code)
    excel_path = fm.get_active_file()

    services.apply_contract_structure_excel.apply_update(
        contract_id=contract.id,
        excel_path=excel_path,
    )

    fm.mark_processed()  # 🔒 DOMKNIĘCIE LIFECYCLE

    print(f"Contract '{contract.code}' updated from Excel.")


# =========================================================
# UTILS
# =========================================================

def _resolve_contract(ref: str, services):
    repo = services.contract_repository

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


# =========================================================
# REGISTRY
# =========================================================

REGISTRY.register_group("apply", build_apply_contract)
