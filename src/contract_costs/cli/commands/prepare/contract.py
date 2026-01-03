import logging
from uuid import UUID

import contract_costs.config as cfg
from contract_costs.cli.context import get_services
from contract_costs.cli.registry import REGISTRY

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

    service = services.generate_contract_structure_excel

    # ---------------- NEW CONTRACT ----------------

    if contract_ref == "new":
        output_path = (
            cfg.INPUTS_CONTRACTS_NEW_DIR /
            cfg.CONTRACT_EXCEL_FILENAME
        )

        if output_path.exists():
            raise RuntimeError(
                f"Contract Excel already exists: {output_path}\n"
                "Apply or remove it before preparing a new one."
            )

        service.generate_empty(output_path)
        logger.info("Empty contract structure Excel generated: %s", output_path)
        print(f"Prepared NEW contract Excel:\n{output_path}")
        return

    # ---------------- EDIT CONTRACT ----------------

    contract = _resolve_contract(contract_ref, services)

    filename = cfg.CONTRACT_EDIT_EXCEL_TEMPLATE.format(code=contract.code)
    output_path = cfg.INPUTS_CONTRACTS_EDIT_DIR / filename

    if output_path.exists():
        raise RuntimeError(
            f"Contract Excel already exists: {output_path}\n"
            "Apply or remove it before preparing again."
        )

    service.generate_from_contract(contract.id, output_path)

    logger.info(
        "Contract structure Excel generated: contract=%s path=%s",
        contract.code,
        output_path,
    )
    print(f"Prepared contract '{contract.code}' for editing:\n{output_path}")


# =========================================================
# UTILS
# =========================================================

def _resolve_contract(contract_ref: str, services):
    repo = services.contract_repository

    try:
        contract = repo.get(UUID(contract_ref))
        if contract:
            return contract
    except ValueError:
        pass

    contract = repo.get_by_code(contract_ref)
    if contract:
        return contract

    raise RuntimeError(f"Contract not found: {contract_ref}")


# =========================================================
# REGISTRY
# =========================================================

REGISTRY.register_group("prepare", build_prepare_contract)
