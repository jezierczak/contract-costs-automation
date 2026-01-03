import logging
from uuid import UUID

import contract_costs.config as cfg
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY

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
        excel_path = (
            cfg.INPUTS_CONTRACTS_NEW_DIR /
            cfg.CONTRACT_EXCEL_FILENAME
        )

        services.apply_contract_structure_excel.apply_new(excel_path)
        print("New contract applied from Excel.")
        return

    contract = _resolve_contract(ref, services)

    filename = cfg.CONTRACT_EDIT_EXCEL_TEMPLATE.format(code=contract.code)
    excel_path = cfg.INPUTS_CONTRACTS_EDIT_DIR / filename

    services.apply_contract_structure_excel.apply_update(
        contract_id=contract.id,
        excel_path=excel_path,
    )

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
