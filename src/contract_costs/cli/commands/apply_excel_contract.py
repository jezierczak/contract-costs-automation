import logging
from pathlib import Path
from datetime import datetime
from uuid import UUID

import contract_costs.config as cfg
from contract_costs.cli.context import get_services

logger = logging.getLogger(__name__)


def handle_applyexcel_contract(ref: str) -> None:
    if ref is None:
        print("Missing contract reference. Use 'new' or contract UUID/code.")
        return

    services = get_services()

    if ref == "new":
        _apply_new_contract(services)
    else:
        _apply_edit_contract(services, ref)


# ---------------- helpers ----------------

def _apply_new_contract(services) -> None:
    excel_path = _find_new_contract_excel()

    services.apply_contract_structure_excel.apply_new(excel_path)

    _move_to_processed(
        excel_path,
        cfg.INPUTS_CONTRACTS_PROCESSED_DIR / "new",
    )

    print("Contract created successfully from Excel.")


def _apply_edit_contract(services, ref: str) -> None:
    contract = _resolve_contract(ref, services.contract_repository)

    excel_path = _find_edit_contract_excel(contract.code)

    services.apply_contract_structure_excel.apply_update(
        contract_id=contract.id,
        excel_path=excel_path,
    )

    _move_to_processed(
        excel_path,
        cfg.INPUTS_CONTRACTS_PROCESSED_DIR / "edit",
    )

    logger.info(f"Contract {contract.code} updated successfully.")


# ---------------- excel finders ----------------

def _find_new_contract_excel() -> Path:
    """
    new → dokładnie jeden plik: contract.xlsx
    """
    path = cfg.INPUTS_CONTRACTS_NEW_DIR / cfg.CONTRACT_EXCEL_FILENAME

    if not path.exists():
        raise RuntimeError(
            f"Expected file '{cfg.CONTRACT_EXCEL_FILENAME}' "
            f"in {cfg.INPUTS_CONTRACTS_NEW_DIR}"
        )

    return path


def _find_edit_contract_excel(contract_code: str) -> Path:
    """
    edit → dokładnie jeden plik: contract_<CODE>.xlsx
    """
    filename = cfg.CONTRACT_EDIT_EXCEL_TEMPLATE.format(code=contract_code)
    path = cfg.INPUTS_CONTRACTS_EDIT_DIR / filename

    if not path.exists():
        raise RuntimeError(
            f"Expected file '{filename}' in {cfg.INPUTS_CONTRACTS_EDIT_DIR}"
        )

    return path


# ---------------- utils ----------------

def _resolve_contract(ref: str, repo):
    try:
        contract_id = UUID(ref)
        contract = repo.get(contract_id)
    except ValueError:
        contract = repo.get_by_code(ref)

    if contract is None:
        raise RuntimeError(f"Contract not found: {ref}")

    return contract


def _move_to_processed(src: Path, base_dir: Path) -> None:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    target_dir = base_dir / timestamp
    target_dir.mkdir(parents=True, exist_ok=True)

    src.replace(target_dir / src.name)
